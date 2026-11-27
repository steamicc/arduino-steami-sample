// Croquis de la page du wiki « Premiers programmes (docs/software/arduino/premiers-programmes.md) ».

// Joue une note tant que le bouton A est appuyé.
void setup() {
  pinMode(A_BUTTON, INPUT_PULLUP);
}

void loop() {
  if (digitalRead(A_BUTTON) == LOW) {
    tone(SPEAKER, 440);  // la 440 Hz
  } else {
    noTone(SPEAKER);
  }
}
