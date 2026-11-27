// Croquis de la page du wiki « Capteurs et écran (docs/software/arduino/capteurs.md) ».

#include <SteamiBoard.h>
#include <SteamiMCP23009E.h>

SteamiMCP23009E dpad(Steami.wire(), RST_EXPANDER, MCP23009_I2C_ADDR, INT_EXPANDER);

const uint8_t boutons[] = {MCP23009_BTN_UP, MCP23009_BTN_DOWN, MCP23009_BTN_LEFT, MCP23009_BTN_RIGHT};
const char* noms[] = {"HAUT", "BAS", "GAUCHE", "DROITE"};

void setup() {
  Serial.begin(115200);
  dpad.begin();
  for (uint8_t i = 0; i < 4; i++) {
    dpad.setup(boutons[i], MCP23009_DIR_INPUT, MCP23009_PULLUP);
  }
}

void loop() {
  for (uint8_t i = 0; i < 4; i++) {
    if (dpad.getLevel(boutons[i]) == MCP23009_LOGIC_LOW) {  // appuyé = niveau bas
      Serial.println(noms[i]);
    }
  }
  delay(100);
}
