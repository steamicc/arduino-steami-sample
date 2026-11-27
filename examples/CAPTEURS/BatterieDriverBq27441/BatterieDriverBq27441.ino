// Croquis de la page du wiki « Capteurs (docs/software/arduino/capteurs.md) ».

#include <SteamiBoard.h>
#include <SteamiBQ27441.h>

SteamiBQ27441 batterie(Steami.wire());

void setup() {
  Serial.begin(115200);
  if (!batterie.begin()) {
    Serial.println("BQ27441 non détecté");
    while (true) {}
  }
}

void loop() {
  Serial.print("Charge : ");
  Serial.print(batterie.stateOfCharge());
  Serial.print(" %  Tension : ");
  Serial.print(batterie.voltageMv());
  Serial.println(" mV");
  delay(2000);
}
