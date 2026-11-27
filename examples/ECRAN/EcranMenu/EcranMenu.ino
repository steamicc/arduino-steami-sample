// Croquis de la page du wiki « Écran (docs/software/arduino/ecran.md) ».

#include <SteamiScreen.h>
#include <SteamiButtons.h>

SteamiScreen ecran;
SteamiButtons boutons;

const char* const ELEMENTS[] = {"Température", "Humidité", "Pression", "Boussole"};
int choix = 0;                          // un int, pas un unsigned ni un size_t

void setup() {
  Serial.begin(115200);
  ecran.begin();
  boutons.begin();
}

void loop() {
  if (boutons.wasPressed(SteamiButton::UP)) {
    choix--;
  }
  if (boutons.wasPressed(SteamiButton::DOWN)) {
    choix++;
  }
  ecran.clear();
  ecran.title("Menu");
  choix = ecran.menu(ELEMENTS, choix);  // -1 devient le dernier élément
  ecran.show();
  delay(20);
}
