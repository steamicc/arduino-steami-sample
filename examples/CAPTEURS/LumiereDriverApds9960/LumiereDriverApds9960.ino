// Croquis de la page du wiki « Capteurs et écran (docs/software/arduino/capteurs.md) ».

#include <SteamiBoard.h>
#include <SteamiAPDS9960.h>

SteamiAPDS9960 lumiere(Steami.wire());

void setup() {
  Serial.begin(115200);
  if (!lumiere.begin()) {
    Serial.println("APDS-9960 non détecté");
    while (true) {}
  }
  lumiere.enableLightSensor();
}

void loop() {
  uint16_t clair;
  if (lumiere.ambientLight(clair)) {
    Serial.print("Lumière ambiante (nombre brut) : ");
    Serial.println(clair);
  }
  delay(500);
}
