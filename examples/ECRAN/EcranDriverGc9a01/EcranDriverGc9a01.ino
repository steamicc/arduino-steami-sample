// Croquis de la page du wiki « Capteurs et écran (docs/software/arduino/capteurs.md) ».

#include <SteamiGC9A01.h>

SteamiGC9A01 affichage;

void setup() {
  Serial.begin(115200);
  if (!affichage.begin()) {               // false si la mémoire manque
    Serial.println("Mémoire insuffisante pour l'écran");
    while (true) {}
  }
  affichage.fill(GC9A01_BLACK);
  affichage.text("Bonjour !", 93, 100, GC9A01_WHITE);
  affichage.fillRect(100, 130, 40, 40, GC9A01_RED);
  affichage.show();                       // envoie l'image à l'écran
}

void loop() {}
