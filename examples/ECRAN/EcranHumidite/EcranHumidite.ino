// Croquis de la page du wiki « Écran (docs/software/arduino/ecran.md) ».

#include <SteamiScreen.h>
#include <SteamiHumidity.h>

SteamiScreen ecran;
SteamiHumidity humidite;

void setup() {
  Serial.begin(115200);
  ecran.begin();                     // en premier, comme pour SteamiDisplay
  humidite.begin();
}

void loop() {
  float h = humidite.read();         // NAN si la mesure manque
  ecran.clear();
  ecran.title("Humidité");           // en haut ; s'affiche sans accent
  ecran.value(h, "%");               // au centre, unité en dessous ; NAN s'écrit --
  ecran.bar(h);                      // barre remplie de 0 à 100, vide pour NAN
  ecran.subtitle(humidite.chip());   // nom du capteur, en bas
  ecran.show();
  delay(1000);
}
