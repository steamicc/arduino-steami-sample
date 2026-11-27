// Croquis de la page du wiki « Capteurs et écran (docs/software/arduino/capteurs.md) ».

#include <SteamiBoard.h>
#include <SteamiWsenPads.h>
#include <SteamiWsenHids.h>

SteamiWsenPads pression(Steami.wire());
SteamiWsenHids humidite(Steami.wire());

void setup() {
  Serial.begin(115200);
  if (!pression.begin() || !humidite.begin()) {
    Serial.println("Capteur non détecté");
    while (true) {}
  }
}

void loop() {
  Serial.print("Pression : ");
  Serial.print(pression.pressureHpa());
  Serial.print(" hPa  Humidité : ");
  Serial.print(humidite.humidity());
  Serial.print(" %  Température : ");
  Serial.print(humidite.temperature());
  Serial.println(" °C");
  delay(1000);
}
