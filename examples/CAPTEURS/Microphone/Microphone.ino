// Croquis de la page du wiki « Capteurs et écran (docs/software/arduino/capteurs.md) ».

#include <SteamiIMP34DT05.h>

SteamiIMP34DT05 micro;

void setup() {
  Serial.begin(115200);
  if (!micro.begin()) {
    Serial.println("Microphone non détecté");
    while (true) {}
  }
  micro.setLevelWindowMs(200);            // un niveau toutes les 200 ms
}

void loop() {
  if (micro.levelReady()) {
    Serial.print("Niveau : ");
    Serial.print(micro.levelDbfs(), 1);
    Serial.println(" dBFS");
  }
}
