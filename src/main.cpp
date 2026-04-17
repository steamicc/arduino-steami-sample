#include <Arduino.h>
// #include "../LED/blink.cpp"
#include "../BUTTON/led_on.cpp"

void setup()
{
  // setup_blink(); /*../LED/blink.cpp*/
  setup_led_on(); /*../BUTTON/led_on.cpp*/
}

void loop()
{
  // loop_blink(); /*../LED/blink.cpp*/
  loop_led_on(); /*../BUTTON/led_on.cpp*/
}
