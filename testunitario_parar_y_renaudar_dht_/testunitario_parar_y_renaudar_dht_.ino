
#include <SoftwareSerial.h>

SoftwareSerial mySerial(10, 11);
long int timerEnvio = 1000;
bool enviar = true;

void setup(){
  Serial.begin(9600);
  mySerial.begin(9600);
}

void loop() {
   if (Serial.available() > 0) {
        String orden = Serial.readStringUntil('\n');
        orden.trim();

        if (orden == "parar") {
            enviar = false;
            Serial.println("Satelite parado"); //Comp
        }
        else if (orden == "reanudar") {
            enviar = true;
            Serial.println("Satelite reanudado"); //Comp
        }
        else {
            Serial.println("Orden invalida"); //Comp
        }
       
    }

}




