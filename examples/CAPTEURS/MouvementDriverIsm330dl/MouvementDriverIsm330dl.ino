// Croquis de la page du wiki « Capteurs et écran (docs/software/arduino/capteurs.md) ».

#include <SteamiBoard.h>
#include <SteamiISM330DL.h>

SteamiISM330DL imu(Steami.wire());

void setup() {
  Serial.begin(115200);
  if (!imu.begin()) {
    Serial.println("ISM330DL non détecté");
    while (true) {}
  }
}

void loop() {
  SteamiISM330DL::Vector3 a;
  if (imu.accelerationG(a)) {
    Serial.print("x=");
    Serial.print(a.x);
    Serial.print(" g  y=");
    Serial.print(a.y);
    Serial.print(" g  z=");
    Serial.print(a.z);
    Serial.println(" g");
  }
  delay(200);
}
