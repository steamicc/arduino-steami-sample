// Croquis de la page du wiki « Écran (docs/software/arduino/ecran.md) ».

#include <SteamiScreen.h>
#include <SteamiHumidity.h>

SteamiScreen ecran;
SteamiHumidity humidite;

void setup() {
  Serial.begin(115200);
  ecran.begin();
  humidite.begin();
}

void loop() {
  float h = humidite.read();
  ecran.clear();
  ecran.gauge(h, 0, 100, STEAMI_BLUE);  // d'abord la jauge : le texte passe par-dessus
  ecran.title("Humidité");
  ecran.value(h, "%");                  // gauge() n'écrit pas la valeur
  ecran.show();
  delay(500);
}
