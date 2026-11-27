// Croquis de la page du wiki « Capteurs et écran (docs/software/arduino/capteurs.md) ».

#include <SteamiLight.h>
#include <SteamiColor.h>

SteamiLight lumiere;
SteamiColor couleur;

void setup() {
  Serial.begin(115200);
  lumiere.begin();
  couleur.begin();
}

void loop() {
  uint16_t rouge, vert, bleu;
  Serial.print("Lumière : ");
  Serial.print(lumiere.read());
  if (couleur.read(rouge, vert, bleu)) {
    Serial.print("  rouge=");
    Serial.print(rouge);
    Serial.print(" vert=");
    Serial.print(vert);
    Serial.print(" bleu=");
    Serial.print(bleu);
  }
  Serial.println();
  delay(500);
}
