// Croquis de la page du wiki « Capteurs (docs/software/arduino/capteurs.md) ».

#include <SteamiBattery.h>

SteamiBattery batterie;

void setup() {
  Serial.begin(115200);
  batterie.begin();
}

void loop() {
  Serial.print("Charge : ");
  Serial.print(batterie.percent());
  Serial.print(" %  Tension : ");
  Serial.print(batterie.voltage());
  Serial.print(" V  Courant : ");
  Serial.print(batterie.current());
  Serial.println(batterie.isCharging() ? " mA (en charge)" : " mA");
  delay(2000);
}
