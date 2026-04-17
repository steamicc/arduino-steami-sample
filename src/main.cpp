#include <Arduino.h>
#include "../LED/blink.cpp"
#include "../BUTTON/led_on.cpp"

void setup() {
//  setup_blink();
  setup_led_on();
}

void loop() {
  // loop_blink();
  loop_led_on();
}
