// Croquis de la page du wiki « Écran (docs/software/arduino/ecran.md) ».

#include <SteamiDisplay.h>

SteamiDisplay ecran;

void setup() {
  Serial.begin(115200);
  if (!ecran.begin()) {                    // en premier : l'image prend beaucoup de mémoire
    Serial.print("Pas d'écran : ");
    Serial.println(ecran.error());
    return;
  }
  const int16_t cx = ecran.centerX(), cy = ecran.centerY();
  ecran.clear();                           // fond noir
  ecran.circle(cx, cy, ecran.radius() - 1, STEAMI_GREEN);
  ecran.text("Bonjour !", cx - ecran.textWidth("Bonjour !") / 2, cy - 4);
  ecran.show();                            // envoie l'image à l'écran
}

void loop() {}
