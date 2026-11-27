// Croquis de la page du wiki « Reconnaître la carte (docs/software/arduino/carte.md) ».

#include <SteamiTemperature.h>
#include <SteamiPressure.h>
#include <SteamiDistance.h>

SteamiTemperature temperature;
SteamiPressure pression;
SteamiDistance distance;

void setup() {
  Serial.begin(115200);
  if (temperature.begin()) {
    Serial.print("Capteur de température : ");
    Serial.println(temperature.chip());  // BME280 sur une V1c
  }
  pression.begin();
  distance.begin();
}

void loop() {
  Serial.print("Température : ");
  Serial.print(temperature.read());
  Serial.print(" °C  Pression : ");
  Serial.print(pression.read());
  Serial.print(" hPa  Altitude : ");
  Serial.print(pression.altitude());
  Serial.print(" m  Distance : ");
  Serial.print(distance.read());
  Serial.println(" mm");
  delay(1000);
}
