// Croquis de la page du wiki « Capteurs (docs/software/arduino/capteurs.md) ».

#include <SteamiBoard.h>
#include <SteamiDaplinkBridge.h>
#include <SteamiDaplinkFlash.h>

SteamiDaplinkBridge pont(Steami.wire());
SteamiDaplinkFlash fichier(pont);

void setup() {
  Serial.begin(115200);
  if (!fichier.begin()) {
    Serial.println("DAPLink non détecté");
    while (true) {}
  }
  if (!fichier.setFilename("MESURES", "CSV")) {
    Serial.println("Nom refusé");
  }
  fichier.writeLine("secondes");          // en-tête : repère chaque démarrage
}

void loop() {
  char ligne[16];
  snprintf(ligne, sizeof(ligne), "%lu", millis() / 1000);
  fichier.writeLine(ligne);               // ajoute une ligne à la fin du fichier
  Serial.println(ligne);
  delay(10000);
}
