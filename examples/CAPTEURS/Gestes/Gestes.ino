// Croquis de la page du wiki « Capteurs (docs/software/arduino/capteurs.md) ».

#include <SteamiGesture.h>

SteamiGesture geste;

void setup() {
  Serial.begin(115200);
  geste.begin();
}

void loop() {
  SteamiGesture::Direction direction = geste.read(200);  // NONE tout de suite si aucune main
  if (direction != SteamiGesture::NONE) {
    Serial.println(SteamiGesture::name(direction));
  }
}
