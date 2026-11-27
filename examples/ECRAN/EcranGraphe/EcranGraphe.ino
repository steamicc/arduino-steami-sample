// Croquis de la page du wiki « Écran (docs/software/arduino/ecran.md) ».

#include <SteamiScreen.h>
#include <SteamiPressure.h>

SteamiScreen ecran;
SteamiPressure pression;
SteamiHistory<30> historique;           // les 30 dernières mesures, sans allocation dynamique

void setup() {
  Serial.begin(115200);
  ecran.begin();                        // en premier, comme pour SteamiDisplay
  pression.begin();
}

void loop() {
  historique.add(pression.read());      // la plus ancienne est oubliée ; NAN laisse un trou
  ecran.clear();
  ecran.title("Pression");
  ecran.graph(historique, 950, 1050);   // dernière valeur, bornes, axes et courbe
  ecran.subtitle(pression.chip());
  ecran.show();
  delay(1000);                          // une mesure par seconde
}
