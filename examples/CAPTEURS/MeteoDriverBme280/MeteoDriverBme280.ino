// Croquis de la page du wiki « Capteurs et écran (docs/software/arduino/capteurs.md) ».

#include <SteamiBoard.h>
#include <SteamiBME280.h>

SteamiBME280 bme(Steami.wire());

void setup() {
  Serial.begin(115200);
  if (!bme.begin()) {
    Serial.println("BME280 non détecté");
    while (true) {}
  }
}

void loop() {
  auto mesure = bme.read();  // les trois grandeurs d'une même mesure
  Serial.print("Température : ");
  Serial.print(mesure.temperature);
  Serial.print(" °C  Humidité : ");
  Serial.print(mesure.humidity);
  Serial.print(" %  Pression : ");
  Serial.print(mesure.pressure);
  Serial.println(" hPa");
  delay(1000);
}
