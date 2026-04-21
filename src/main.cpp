#include <Arduino.h>
// #include "../LED/blink.cpp"
#include "../BUTTON/led_toggle.cpp"

void setup()
{
  // setup_blink(); /*../LED/blink.cpp*/
  setup_led_toggle(); /*../BUTTON/led_toggle.cpp*/
}

void loop()
{
  // loop_blink(); /*../LED/blink.cpp*/
  loop_led_toggle(); /*../BUTTON/led_toggle.cpp*/
}
