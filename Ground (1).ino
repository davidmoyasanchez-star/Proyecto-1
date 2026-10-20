#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11); // RX, TX 
long int timer=5000;
bool error=false;
int timeout=5000;
unsigned long ultimoMensaje = 0;
const unsigned long TIMEOUT = 3000;
bool stateled1 = LOW;
const int led1=7;
void setup() {
   Serial.begin(9600);
   mySerial.begin(9600);
}

void loop() {
   digitalWrite(led1,stateled1);
   // LECTURA DE DATOS DEL SATÉLITE 
    if (millis() - ultimoMensaje > TIMEOUT) { // Alerta de error de comunicacion
        Serial.println("Error de recepcion");
        ultimoMensaje = millis(); // evita spam del mensaje
        stateled1=HIGH;
    }

   else if (mySerial.available() > 0) {
      String data = mySerial.readStringUntil('\n');
      data.trim();
         if (data.length() == 0) {
            return;
         }

         if (data == "error") {
            Serial.println("Alerta: error de sensor");
            ultimoMensaje = millis();
            stateled1=HIGH;
         }
         else {
            Serial.println(data);
            ultimoMensaje = millis();
         }
   }

   // ENVÍO DE ÓRDENES DESDE EL MONITOR SERIE 
   if (Serial.available() > 0) {
      String orden = Serial.readStringUntil('\n');
      orden.trim();

      if (orden.length() > 0) {
         mySerial.println(orden);
         Serial.println("Orden enviada: " + orden);
      }
   }
}
