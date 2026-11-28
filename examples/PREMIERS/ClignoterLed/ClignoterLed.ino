// Croquis de la page du wiki « Premiers programmes (docs/software/arduino/premiers-programmes.md) ».

// Fait clignoter la LED RGB en rouge, vert puis bleu.
void setup() {
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);
  Serial.begin(115200);
}

void loop() {
  digitalWrite(LED_RED, HIGH);
  Serial.println("Rouge");
  delay(500);
  digitalWrite(LED_RED, LOW);

  digitalWrite(LED_GREEN, HIGH);
  Serial.println("Vert");
  delay(500);
  digitalWrite(LED_GREEN, LOW);

  digitalWrite(LED_BLUE, HIGH);
  Serial.println("Bleu");
  delay(500);
  digitalWrite(LED_BLUE, LOW);
}
// mesure CI
