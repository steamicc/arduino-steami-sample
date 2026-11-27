// Croquis de la page du wiki « Capteurs et écran (docs/software/arduino/capteurs.md) ».

#include <SteamiDistance.h>

SteamiDistance distance;

void setup() {
  Serial.begin(115200);
  distance.begin();
}

void loop() {
  Serial.print("Distance : ");
  Serial.print(distance.read());
  Serial.println(" mm");
  delay(500);
}
