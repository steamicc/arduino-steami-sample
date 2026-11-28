// Croquis de la page du wiki « Capteurs (docs/software/arduino/capteurs.md) ».

#include <SteamiCompass.h>
#include <SteamiButtons.h>

SteamiCompass boussole;
SteamiButtons boutons;

unsigned long dernierAffichage = 0;

void afficherCap(float cap) {
  if (isnan(cap)) {
    Serial.print("nan");
  } else {
    Serial.print(lroundf(cap) % 360);  // arrondi au degré : 359,6 s'affiche 0, jamais 360
  }
  Serial.print(" deg");
}

void setup() {
  Serial.begin(115200);
  boussole.begin();
  boutons.begin();
}

void loop() {
  // lire les boutons souvent : une tape brève dure environ 100 ms
  if (boutons.wasPressed(SteamiButton::MENU)) {
    Serial.println("Calibration : tourner la carte dans tous les sens pendant 12 s");
    boussole.calibrate(12);
    Serial.println("Calibration terminée. Pencher la carte sans la tourner.");
  }

  if (millis() - dernierAffichage >= 500) {  // affichage deux fois par seconde
    dernierAffichage = millis();
    Serial.print("à plat : ");
    afficherCap(boussole.heading());
    Serial.print("   compensé : ");
    afficherCap(boussole.headingTiltCompensated());
    Serial.println();
  }
  delay(5);
}
