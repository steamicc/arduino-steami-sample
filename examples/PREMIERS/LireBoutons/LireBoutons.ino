// Croquis de la page du wiki « Premiers programmes (docs/software/arduino/premiers-programmes.md) ».

// A allume le rouge, B le vert, MENU le bleu.
void setup() {
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);

  // Un bouton appuyé relie la broche à la masse : on active le pull-up interne.
  pinMode(A_BUTTON, INPUT_PULLUP);
  pinMode(B_BUTTON, INPUT_PULLUP);
  pinMode(MENU_BUTTON, INPUT_PULLUP);
}

void loop() {
  digitalWrite(LED_RED, digitalRead(A_BUTTON) == LOW);
  digitalWrite(LED_GREEN, digitalRead(B_BUTTON) == LOW);
  digitalWrite(LED_BLUE, digitalRead(MENU_BUTTON) == LOW);
}
