// Croquis de la page du wiki « Capteurs (docs/software/arduino/capteurs.md) ».

#include <SteamiButtons.h>

SteamiButtons boutons;

const SteamiButton liste[] = {SteamiButton::A, SteamiButton::B, SteamiButton::MENU,
                              SteamiButton::UP, SteamiButton::DOWN,
                              SteamiButton::LEFT, SteamiButton::RIGHT};
const char* noms[] = {"A", "B", "MENU", "HAUT", "BAS", "GAUCHE", "DROITE"};

void setup() {
  Serial.begin(115200);
  boutons.begin();
}

void loop() {
  for (uint8_t i = 0; i < 7; i++) {
    if (boutons.wasPressed(liste[i])) {  // une seule fois par appui
      Serial.println(noms[i]);
    }
  }
  delay(5);  // lire les boutons souvent : une tape brève dure environ 100 ms
}
