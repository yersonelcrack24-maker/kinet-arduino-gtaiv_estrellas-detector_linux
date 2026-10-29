#include "MCreatorLink.h"

int led = 8;    // LED 1
int led2 = 9;   // LED 2

void setup() {
    Serial.begin(115200);
    Serial.setTimeout(0);
    MCreatorLink.setup(Serial);
    pinMode(led, OUTPUT);
    digitalWrite(led, LOW);
    pinMode(led2, OUTPUT);
    digitalWrite(led2, LOW);
}

void loop() {
    if (Serial.available() > 0) {
        char c = Serial.read();
        
        if (c == 'l') {
            digitalWrite(led, HIGH);
        } 
        else if (c == 'k') {
            digitalWrite(led, LOW);
        }
        else if (c == 'n') {
            digitalWrite(led2, HIGH);
        } 
        else if (c == 'p' || c == 'm') {
            digitalWrite(led2, LOW);
        } else {
            MCreatorLink.loop();
        }
    } else {
        MCreatorLink.loop();
    }
}
