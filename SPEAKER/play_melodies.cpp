#include <Arduino.h>

void setup_buzzer()
{
    Serial.begin(115200);
    delay(200);

    pinMode(A_BUTTON, INPUT_PULLUP);
    pinMode(B_BUTTON, INPUT_PULLUP);
    pinMode(MENU_BUTTON, INPUT_PULLUP);

    pinMode(SPEAKER, OUTPUT);
}

struct Note
{
    int freq;
    int time;
};

const Note happy_sound[] = {
    {523, 200}, {659, 200}, {784, 300}, {659, 200}, {784, 200}, {880, 300}, {0, 100}, {784, 150}, {880, 150}, {988, 400}, {0, 100}, {880, 200}, {784, 200}, {659, 300}};

const Note sad_sound[] = {
    {659, 400}, {0, 100}, {587, 300}, {0, 100}, {523, 500}, {0, 100}, {494, 400}, {523, 600}, {0, 200}, {440, 300}, {392, 600}, {0, 200}, {440, 300}};

const Note epic_sound[] = {
    {440, 100}, {523, 100}, {659, 200}, {784, 200}, {988, 300}, {880, 100}, {784, 100}, {659, 200}, {0, 100}, {659, 100}, {784, 100}, {988, 300}, {1047, 400}, {988, 150}, {880, 150}, {784, 300}};

void play_sound(const Note* sound, size_t note_count)
{
    if (sound != NULL)
    {
        for (size_t i = 0; i < note_count; i++)
        {
            if (sound[i].freq > 0){
            tone(SPEAKER, sound[i].freq, sound[i].time);
            delay(sound[i].time);
            noTone(SPEAKER);
            }
            else{
                noTone(SPEAKER);
            }
        }
    }
}

void loop_buzzer()
{
    Note *sound = NULL;
    int size = 0;

    if (digitalRead(A_BUTTON) == LOW)
    {
        Serial.println("Happy sound");
        sound = happy_sound;
        size = sizeof(happy_sound);
        play_sound(happy_sound, sizeof(happy_sound)/sizeof(Note));
    }
    else if (digitalRead(B_BUTTON) == LOW)
    {
        Serial.println("sad sound");
        sound = sad_sound;
        size = sizeof(sad_sound);
        play_sound(sad_sound, sizeof(sad_sound)/sizeof(Note));
    }
    else if (digitalRead(MENU_BUTTON) == LOW)
    {
        Serial.println("epic sound");
        sound = epic_sound;
        size = sizeof(epic_sound);
        play_sound(epic_sound, sizeof(epic_sound)/sizeof(Note));
    }
    delay(100);
}
