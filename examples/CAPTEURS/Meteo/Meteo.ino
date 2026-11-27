// Croquis de la page du wiki « Capteurs et écran (docs/software/arduino/capteurs.md) ».

#include <SteamiTemperature.h>
#include <SteamiHumidity.h>
#include <SteamiPressure.h>

SteamiTemperature temperature;
SteamiHumidity humidite;
SteamiPressure pression;

void setup() {
  Serial.begin(115200);
  temperature.begin();
  humidite.begin();
  pression.begin();
}

void loop() {
  Serial.print("Température : ");
  Serial.print(temperature.read());
  Serial.print(" °C  Humidité : ");
  Serial.print(humidite.read());
  Serial.print(" %  Pression : ");
  Serial.print(pression.read());
  Serial.print(" hPa  Altitude : ");
  Serial.print(pression.altitude());
  Serial.println(" m");
  delay(1000);
}
