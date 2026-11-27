// Croquis de la page du wiki « Reconnaître la carte (docs/software/arduino/carte.md) ».

#include <SteamiBoard.h>
#include <SteamiDaplinkBridge.h>
#include <SteamiDaplinkFlash.h>

SteamiDaplinkBridge pont(Steami.wire());  // le bus interne de la carte
SteamiDaplinkFlash fichier(pont);

void setup() {
  Serial.begin(115200);
  if (!fichier.begin()) {
    Serial.println("DAPLink non détecté");
    while (true) {}
  }
}

void loop() {
  SteamiDaplinkFlash::Filename nom;
  if (fichier.getFilename(nom)) {
    Serial.print("Fichier du disque USB : ");
    Serial.print(nom.name);
    Serial.print('.');
    Serial.println(nom.ext);
  }
  delay(1000);
}
