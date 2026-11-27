// Croquis de la page du wiki « Capteurs (docs/software/arduino/capteurs.md) ».

#include <SteamiAccelerometer.h>
#include <SteamiGyroscope.h>

SteamiAccelerometer acceleration;
SteamiGyroscope rotation;

void setup() {
  Serial.begin(115200);
  acceleration.begin();
  rotation.begin();
}

void loop() {
  SteamiVector a = acceleration.read();  // les trois axes, en g
  Serial.print("x=");
  Serial.print(a.x);
  Serial.print(" g  y=");
  Serial.print(a.y);
  Serial.print(" g  z=");
  Serial.print(a.z);
  Serial.print(" g  rotation autour de z : ");
  Serial.print(rotation.z());
  Serial.print(" deg/s");
  if (acceleration.isShaken()) {
    Serial.print("  secousse !");
  }
  Serial.println();
  delay(200);
}
