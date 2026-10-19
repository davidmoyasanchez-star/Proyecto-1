#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11); // RX, TX 
unsigned long nextMillis = 5000;
bool error=false;

void setup() {
   Serial.begin(9600);
   mySerial.begin(9600);
}
void loop() {
   if (mySerial.available()) {
      String data = mySerial.readString();
      data.trim();
      if ((millis()==nextMillis) && (data=="\n")){
         error=true;
         nextMillis=nextMillis+5000;
         if((error==true) && (millis()==nextMillis)){
            Serial.print("error de comunicacion");
         }
      }
      else{
         if (data=="error"){
            Serial.print("Alerta");
         }
         else{
            Serial.print(data);
            }
         }
      String orden = Serial.readStringUntil('\n');
      mySerial.println(orden);
   }
}
