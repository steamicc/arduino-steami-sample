// Croquis de la page du wiki « Capteurs et écran (docs/software/arduino/capteurs.md) ».

#include <SteamiSSD1327.h>

SteamiSSD1327 oled;

void setup() {
  oled.begin();
  oled.fill(0);                       // 0 = noir, 15 = blanc
  oled.text("Bonjour !", 30, 60, 15);
  oled.show();                        // envoie l'image à l'écran
}

void loop() {}
