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
   // LECTURA DE DATOS DEL SATÉLITE 
    if (millis() - ultimoMensaje > TIMEOUT) { // Alerta de error de comunicacion
        Serial.println("error:5");
        ultimoMensaje = millis(); // evita spam del mensaje
        stateled1=HIGH;
    }

   else if (mySerial.available() > 0) {
      String data = mySerial.readStringUntil('\n');
      data.trim();
         if (data.length() == 0) { // Ignorar basura como espacios en blanco, etc
            return;
         }
            Serial.println(data);
            ultimoMensaje = millis();
   }

   // ENVÍO DE ÓRDENES DESDE EL MONITOR SERIE 
   if (Serial.available() > 0) {
      String orden = Serial.readStringUntil('\n'); // Leer orden de la interfaz
      orden.trim(); // Recortar la orden para eliminar espacios en blanco al principio y/o al final

      if (orden.length() > 0) { // Para que no envie espacios en blanco
         mySerial.println(orden);
         Serial.println("Orden enviada: " + orden);
      }
   }
}
