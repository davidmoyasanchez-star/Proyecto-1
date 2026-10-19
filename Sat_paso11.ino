#include <DHT.h>
#define DHTPIN 2
#define DHTTYPE DHT11
#include <SoftwareSerial.h>

DHT dht(DHTPIN, DHTTYPE);
SoftwareSerial mySerial(10, 11); // RX, TX 

long int timerEnvio = 1000;
bool enviar = true;

void setup() {
    Serial.begin(9600);
    mySerial.begin(9600);
    dht.begin();
}

void loop() {

    // -------- LECTURA NO BLOQUEANTE --------
    if (mySerial.available() > 0) {
        String orden = mySerial.readStringUntil('\n');
        orden.trim();

        if (orden == "parar") {
            enviar = false;
            Serial.println("Satelite parado");
        }
        else if (orden == "reanudar") {
            enviar = true;
            Serial.println("Satelite reanudado");
        }
        else {
            Serial.println("Orden invalida");
        }
    }
    // ---------------------------------------

    float t = dht.readTemperature();
    float h = dht.readHumidity();

    if (isnan(t) || isnan(h)) {
        Serial.println("Error sensor");
        mySerial.println("error");
        return;
    }

    if (enviar) {
        if (millis() >= timerEnvio) {
            mySerial.print("T:");
            mySerial.print(t);
            mySerial.print(":H:");
            mySerial.println(h);

            timerEnvio += 1000;
        }
    }
}

