#include <Arduino.h>

void setup_led_on()
{
    Serial.begin(115200);
    delay(2000);

    pinMode(LED_RED, OUTPUT);
    pinMode(LED_BLUE, OUTPUT);
    pinMode(LED_GREEN, OUTPUT);

    pinMode(A_BUTTON, INPUT_PULLUP);
    pinMode(B_BUTTON, INPUT_PULLUP);
    pinMode(MENU_BUTTON, INPUT_PULLUP);
}

void loop_led_on()
{
    
    if (digitalRead(A_BUTTON) == LOW)
    {
        Serial.println("A_BUTTON pressed\n");
        digitalWrite(LED_RED, HIGH);
        delay(200);
        digitalWrite(LED_RED, LOW);
    }
    else if (digitalRead(B_BUTTON) == LOW)
    {
        Serial.println("B_BUTTON pressed\n");
        digitalWrite(LED_GREEN, HIGH);
        delay(200);
        digitalWrite(LED_GREEN, LOW);
    }
    else if (digitalRead(MENU_BUTTON) == LOW)
    {
        Serial.println("MENU_BUTTON pressed\n");
        digitalWrite(LED_BLUE, HIGH);
        delay(200);
        digitalWrite(LED_BLUE, LOW);
    }
}