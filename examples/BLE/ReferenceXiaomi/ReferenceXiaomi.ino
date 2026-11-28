// Référence BLE : la carte compare sa température et son humidité à celles
// d'un thermo-hygromètre Xiaomi LYWSD03MMC posé près d'elle, reçues par BLE.
//
// Le Xiaomi doit avoir le micrologiciel pvvx (https://github.com/pvvx/ATC_MiThermometer),
// dans l'un de ses formats : « custom » (pvvx), « atc1441 » ou BTHome v2 non chiffré.
// Le micrologiciel Xiaomi d'origine chiffre ses données : il est signalé, pas lu.
//
// La carte s'échauffe en fonctionnant : son capteur mesure un air plus chaud, donc
// plus sec en humidité relative, que celui de la pièce. Son humidité se compare donc
// à « HR à Tc », l'humidité qu'aurait l'air du Xiaomi à la température de la carte
// (formule de Magnus). Une ligne CSV part sur le port série toutes les 5 secondes.

#include <STM32duinoBLE.h>
#include <SteamiScreen.h>
#include <SteamiTemperature.h>
#include <SteamiHumidity.h>
#include <math.h>

const char CIBLE[] = "";             // "" : le Xiaomi le plus proche ; sinon adresse MAC ou nom BLE
const uint32_t OUBLI_MS = 60000;     // un capteur muet depuis plus longtemps n'est plus choisi ; les
                                     // trames arrivent par à-coups (5 à 15 s) pendant les rafraîchissements de l'écran
const uint32_t PERIODE_CSV_MS = 5000;
const int HYSTERESIS = 6;            // dB : un autre capteur doit être nettement plus fort
const int MAX_CAPTEURS = 8;

struct Capteur {
  bool utilise;
  char adresse[18];
  char nom[21];
  const char* format;
  int rssi;
  uint32_t vu;
  float temperature;
  float humidite;
};

Capteur capteurs[MAX_CAPTEURS];
int suivi = -1;                      // indice du capteur affiché

SteamiScreen ecran;
SteamiTemperature temperature;
SteamiHumidity humidite;

// --- Décodage des trames publicitaires ------------------------------------

struct Mesure {
  const char* format;
  char mac[18];                      // vide en BTHome : prendre l'adresse BLE
  float temperature;
  float humidite;
};

static int16_t i16le(const uint8_t* p) { return (int16_t)(p[0] | (p[1] << 8)); }
static uint16_t u16le(const uint8_t* p) { return (uint16_t)(p[0] | (p[1] << 8)); }
static int16_t i16be(const uint8_t* p) { return (int16_t)((p[0] << 8) | p[1]); }

static void ecrireMac(char mac[18], const uint8_t* octets, bool inverse) {
  for (int i = 0; i < 6; i++) {
    snprintf(mac + 3 * i, 4, i < 5 ? "%02X:" : "%02X", octets[inverse ? 5 - i : i]);
  }
}

// BTHome v2 : taille des données de chaque objet, -1 si l'objet est inconnu.
static int tailleBthome(uint8_t id) {
  if (id >= 0x15 && id <= 0x2F) return 1;  // capteurs binaires, humidité entière, humidité du sol
  switch (id) {
    case 0x00: case 0x01: case 0x09: case 0x0F: case 0x10: case 0x11: case 0x3A: case 0x46:
      return 1;
    case 0x02: case 0x03: case 0x06: case 0x07: case 0x08: case 0x0C: case 0x0D: case 0x0E:
    case 0x12: case 0x13: case 0x14: case 0x3F: case 0x40: case 0x41: case 0x43: case 0x44:
    case 0x45: case 0x47: case 0x48: case 0x49: case 0x4A: case 0x51: case 0x52:
      return 2;
    case 0x04: case 0x05: case 0x0A: case 0x0B: case 0x42: case 0x4B:
      return 3;
    case 0x4C: case 0x4D: case 0x4E: case 0x4F: case 0x50:
      return 4;
    default:
      return -1;
  }
}

static bool lireBthome(const uint8_t* d, int n, Mesure& m) {
  if (n < 1 || (d[0] & 0x01)) return false;  // vide ou chiffré
  m.format = "bthome";
  m.mac[0] = '\0';
  int i = 1;
  while (i < n) {
    int taille = tailleBthome(d[i]);
    if (taille < 0 || i + 1 + taille > n) break;  // inconnu ou tronqué : on garde ce qui précède
    const uint8_t* v = d + i + 1;
    switch (d[i]) {
      case 0x02: m.temperature = i16le(v) / 100.0f; break;
      case 0x45: m.temperature = i16le(v) / 10.0f; break;
      case 0x03: m.humidite = u16le(v) / 100.0f; break;
      case 0x2E: m.humidite = v[0]; break;
    }
    i += 1 + taille;
  }
  return !isnan(m.temperature) || !isnan(m.humidite);
}

// Vrai si la trame vient d'un thermomètre ; m.format vaut "mibeacon" pour le
// micrologiciel d'origine, illisible.
bool decoder(const uint8_t* trame, int n, Mesure& m) {
  m.temperature = NAN;
  m.humidite = NAN;
  int i = 0;
  while (i + 1 < n) {
    int longueur = trame[i];
    if (longueur == 0 || i + 1 + longueur > n) break;
    if (trame[i + 1] == 0x16 && longueur >= 3) {  // données de service
      uint16_t uuid = trame[i + 2] | (trame[i + 3] << 8);
      const uint8_t* d = trame + i + 4;
      int dn = longueur - 3;
      if (uuid == 0x181A && dn >= 15) {             // pvvx : MAC à l'envers, petit-boutiste
        m.format = "pvvx";
        ecrireMac(m.mac, d, true);
        m.temperature = i16le(d + 6) / 100.0f;
        m.humidite = u16le(d + 8) / 100.0f;
        return true;
      }
      if (uuid == 0x181A && dn >= 13) {             // atc1441 : gros-boutiste
        m.format = "atc1441";
        ecrireMac(m.mac, d, false);
        m.temperature = i16be(d + 6) / 10.0f;
        m.humidite = d[8];
        return true;
      }
      if (uuid == 0xFCD2 && lireBthome(d, dn, m)) return true;
      if (uuid == 0xFE95) {
        m.format = "mibeacon";
        m.mac[0] = '\0';
        return true;
      }
    }
    i += 1 + longueur;
  }
  return false;
}

// Humidité relative (%) qu'aurait l'air de la référence porté à tCible °C.
float humiditeRamenee(float tRef, float hRef, float tCible) {
  if (isnan(tRef) || isnan(hRef) || isnan(tCible)) return NAN;
  auto saturante = [](float t) { return 6.112f * expf(17.62f * t / (243.12f + t)); };
  return hRef * saturante(tRef) / saturante(tCible);
}

// --- Suivi des capteurs ----------------------------------------------------

void noter(const char* adresse, const char* nom, int rssi, const Mesure& m) {
  int libre = -1, plusVieux = 0;
  for (int i = 0; i < MAX_CAPTEURS; i++) {
    if (capteurs[i].utilise && strcmp(capteurs[i].adresse, adresse) == 0) { libre = i; break; }
    if (!capteurs[i].utilise && libre < 0) libre = i;
    if (capteurs[i].vu < capteurs[plusVieux].vu) plusVieux = i;
  }
  if (libre < 0) libre = plusVieux;
  Capteur& c = capteurs[libre];
  bool nouveau = !c.utilise || strcmp(c.adresse, adresse) != 0;
  if (nouveau) {
    c = Capteur{};
    c.utilise = true;
    strncpy(c.adresse, adresse, sizeof c.adresse - 1);
    Serial.print("# capteur ");
    Serial.print(adresse);
    Serial.print(" ");
    Serial.print(nom[0] ? nom : "?");
    Serial.print(" ");
    Serial.println(m.format);
    if (libre == suivi) suivi = -1;
  }
  if (nom[0]) strncpy(c.nom, nom, sizeof c.nom - 1);
  c.format = m.format;
  c.rssi = rssi;
  c.vu = millis();
  c.temperature = m.temperature;
  c.humidite = m.humidite;
}

bool vivant(int i) {
  return capteurs[i].utilise && strcmp(capteurs[i].format, "mibeacon") != 0
         && !isnan(capteurs[i].temperature) && millis() - capteurs[i].vu <= OUBLI_MS;
}

int choisir() {
  if (CIBLE[0]) {
    for (int i = 0; i < MAX_CAPTEURS; i++) {
      if (vivant(i) && (strcasecmp(capteurs[i].adresse, CIBLE) == 0 || strcasecmp(capteurs[i].nom, CIBLE) == 0)) return i;
    }
    return -1;
  }
  int meilleur = -1;
  for (int i = 0; i < MAX_CAPTEURS; i++) {
    if (vivant(i) && (meilleur < 0 || capteurs[i].rssi > capteurs[meilleur].rssi)) meilleur = i;
  }
  if (meilleur < 0) return -1;
  // deux capteurs côte à côte ont presque le même RSSI : garder le capteur suivi
  if (suivi < 0 || !vivant(suivi) || capteurs[meilleur].rssi >= capteurs[suivi].rssi + HYSTERESIS) suivi = meilleur;
  return suivi;
}

void ecouter() {
  BLEDevice d = BLE.available();
  while (d) {
    uint8_t trame[31];
    int n = d.advertisementData(trame, sizeof trame);
    Mesure m;
    if (n > 0 && decoder(trame, n, m)) {
      char adresse[18];
      if (m.mac[0]) {
        strcpy(adresse, m.mac);
      } else {
        String a = d.address();
        a.toUpperCase();
        strncpy(adresse, a.c_str(), sizeof adresse - 1);
        adresse[sizeof adresse - 1] = '\0';
      }
      String nom = d.hasLocalName() ? d.localName() : String("");
      noter(adresse, nom.c_str(), d.rssi(), m);
    }
    d = BLE.available();
  }
}

// --- Affichage ---------------------------------------------------------------

void ligne(const String& s, int y128, SteamiRgb couleur = STEAMI_WHITE) {
  int x = (ecran.width() - ecran.textWidth(s.c_str())) / 2;
  ecran.text(s.c_str(), x, (int16_t)(y128 * ecran.width() / 128), couleur);
}

String nombre(float v, const char* unite) {
  return isnan(v) ? String("--") + unite : String(v, 1) + unite;
}

String ecart(float a, float b, const char* unite) {
  if (isnan(a) || isnan(b)) return "--";
  float d = a - b;
  return (d >= 0 ? "+" : "") + String(d, 1) + unite;
}

void csv(float v) {
  if (!isnan(v)) Serial.print(v, 2);
  Serial.print(";");
}

void setup() {
  Serial.begin(115200);
  ecran.begin();                     // en premier, comme pour SteamiDisplay
  temperature.begin();
  humidite.begin();
  if (!BLE.begin()) {
    Serial.println("BLE indisponible : vérifier la pile radio de la carte");
  }
  BLE.scan(true);                    // avec les doublons : chaque nouvelle mesure arrive
  Serial.println("t_s;adresse;rssi;format;T_ref;HR_ref;T_carte;HR_carte;HR_ref_a_T_carte");
}

void loop() {
  static uint32_t dernierAffichage = 0, dernierCsv = 0;
  ecouter();
  if (millis() - dernierAffichage < 1000) return;
  dernierAffichage = millis();

  float tCarte = temperature.read(), hCarte = humidite.read();
  int i = choisir();
  ecran.clear();
  ecran.title("Référence BLE");
  ligne("Carte", 30, STEAMI_GRAY);
  ligne(nombre(tCarte, "C") + " " + nombre(hCarte, "%"), 39);
  if (i < 0) {
    ligne("Xiaomi ?", 60, STEAMI_GRAY);
    ligne("recherche...", 70, STEAMI_DARK);
  } else {
    Capteur& c = capteurs[i];
    float hRamenee = humiditeRamenee(c.temperature, c.humidite, tCarte);
    ligne(c.nom[0] ? c.nom : c.adresse + 9, 52, STEAMI_GRAY);
    ligne(nombre(c.temperature, "C") + " " + nombre(c.humidite, "%"), 61);
    ligne("HR à Tc " + nombre(hRamenee, "%"), 70, STEAMI_GRAY);
    ligne("Ecart", 82, STEAMI_GRAY);
    ligne(ecart(tCarte, c.temperature, "C") + " " + ecart(hCarte, hRamenee, "%"), 91);
    ligne(String(c.rssi) + "dB " + String((millis() - c.vu) / 1000) + "s", 104, STEAMI_DARK);
    if (millis() - dernierCsv >= PERIODE_CSV_MS) {
      dernierCsv = millis();
      Serial.print(millis() / 1000);
      Serial.print(";");
      Serial.print(c.adresse);
      Serial.print(";");
      Serial.print(c.rssi);
      Serial.print(";");
      Serial.print(c.format);
      Serial.print(";");
      csv(c.temperature);
      csv(c.humidite);
      csv(tCarte);
      csv(hCarte);
      if (!isnan(hRamenee)) Serial.print(hRamenee, 2);
      Serial.println();
    }
  }
  ecran.show();
}
