// Croquis de la page du wiki « Capteurs (docs/software/arduino/capteurs.md) ».

#include <SteamiBoard.h>
#include <SteamiLIS2MDL.h>

SteamiLIS2MDL mag(Steami.wire());

void setup() {
  Serial.begin(115200);
  if (!mag.begin()) {
    Serial.println("LIS2MDL non détecté");
    while (true) {}
  }
}

void loop() {
  float cap = mag.headingFlatOnly();  // carte posée à plat
  Serial.print("Cap : ");
  Serial.print(lroundf(cap) % 360);  // arrondi au degré, jamais 360
  Serial.print(" deg (");
  Serial.print(mag.directionLabel(cap));
  Serial.println(")");
  delay(500);
}
