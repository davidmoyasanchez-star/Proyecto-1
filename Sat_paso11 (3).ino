#include <DHT.h>
#define DHTPIN 2
#define DHTTYPE DHT11
#include <SoftwareSerial.h>

DHT dht(DHTPIN, DHTTYPE);
SoftwareSerial mySerial(10, 11); // RX, TX 
long int timeout= 5000;
long int timerEnvio = 1000;
bool enviar = true;
bool error = false;


void setup() {
    Serial.begin(9600);
    mySerial.begin(9600);
    dht.begin();
}

void loop() {
    if (mySerial.available() > 0) {
        String orden = mySerial.readStringUntil('\n');
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
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    if (isnan(t) || isnan(h)) {
        error=true; 
        int currentmillis=millis();
        timeout=timeout+currentmillis;
        if ((error==true) && (millis()>=timeout)){
            mySerial.println("error");
            Serial.println("error"); //Comp
        }
        return;
    }

    if (enviar) {
        if (millis() >= timerEnvio) {
            Serial.println("Enviando"); //Comp
            mySerial.print("T:");
            mySerial.print(t);
            mySerial.print(":H:");
            mySerial.println(h);

            timerEnvio += 1000;
        }
    }
}

