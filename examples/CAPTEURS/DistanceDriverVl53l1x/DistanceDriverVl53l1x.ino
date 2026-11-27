// Croquis de la page du wiki « Capteurs (docs/software/arduino/capteurs.md) ».

#include <SteamiBoard.h>
#include <SteamiVL53L1X.h>

SteamiVL53L1X tof(Steami.wire());

void setup() {
  Serial.begin(115200);
  if (!tof.begin()) {
    Serial.println("VL53L1X non détecté");
    while (true) {}
  }
  tof.startRanging();
}

void loop() {
  if (tof.dataReady()) {
    Serial.print("Distance : ");
    Serial.print(tof.distanceMm());
    Serial.println(" mm");
  }
  delay(50);
}
