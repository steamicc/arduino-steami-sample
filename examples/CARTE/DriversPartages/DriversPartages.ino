// Croquis de la page du wiki « Reconnaître la carte (docs/software/arduino/carte.md) ».

#include <SteamiBoard.h>

void setup() {
  Serial.begin(115200);
  Steami.begin();
  if (!Steami.has(SteamiFunction::LIGHT)) {
    Serial.println("Pas de capteur de lumière sur cette carte");
  }
}

void loop() {
  float temperature = NAN;
  if (Steami.isV1c()) {
    if (Steami.claim(SteamiChip::BME280) == SteamiStatus::OK) {
      temperature = Steami.bme280()->temperature();
    }
  } else if (Steami.claim(SteamiChip::WSEN_HIDS) == SteamiStatus::OK) {
    temperature = Steami.wsenHids()->temperature();
  }

  Serial.print("Température : ");
  Serial.print(temperature);
  Serial.println(" °C");
  delay(1000);
}
