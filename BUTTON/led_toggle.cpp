#include <Arduino.h>

void setup_led_toggle()
{
    Serial.begin(115200);


    pinMode(LED_RED, OUTPUT);
    pinMode(LED_BLUE, OUTPUT);
    pinMode(LED_GREEN, OUTPUT);

    pinMode(A_BUTTON, INPUT_PULLUP);
    pinMode(B_BUTTON, INPUT_PULLUP);
    pinMode(MENU_BUTTON, INPUT_PULLUP);
}

void loop_led_toggle()
{
    static int previous_a_state = HIGH;
    static int previous_b_state = HIGH;
    static int previous_menu_state = HIGH;

    int current_a = digitalRead(A_BUTTON);
    int current_b = digitalRead(B_BUTTON);
    int current_menu = digitalRead(MENU_BUTTON);

    if (current_a == LOW && previous_a_state == HIGH)
    {
        int led_red_State = !digitalRead(LED_RED);
        Serial.println("A_BUTTON pressed");
        digitalWrite(LED_RED, led_red_State);
    }
    else if (current_b == LOW && previous_b_state == HIGH)
    {
        Serial.println("B_BUTTON pressed");
        int led_green_State = !digitalRead(LED_GREEN);
        digitalWrite(LED_GREEN, led_green_State);
    }
    else if (current_menu == LOW && previous_menu_state == HIGH)
    {
        Serial.println("MENU_BUTTON pressed");
        int led_blue_State = !digitalRead(LED_BLUE);
        digitalWrite(LED_BLUE, led_blue_State);
    }

    previous_a_state = current_a;
    previous_b_state = current_b;
    previous_menu_state = current_menu;
}