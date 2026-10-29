#include "MCreatorLink.h"
int led = 8;
int opcion;
void setup() {
    Serial.begin(115200);
    Serial.setTimeout(20);
    MCreatorLink.setup(Serial);
    pinMode(led, OUTPUT);
}

void loop() {
    if (Serial.available() > 0) {
      opcion = Serial.read();
      if (opcion == 'l'){
        digitalWrite(led, HIGH);}
        
        if (opcion == 'p'){
          digitalWrite(led, LOW);
        }
      }
    MCreatorLink.loop();
}
