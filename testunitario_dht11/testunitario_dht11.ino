#include <DHT.h>
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  delay(2000);
  
  float t = dht.readTemperature();
  float h = dht.readHumidity();

  if (isnan(t) || isnan(h)) {
    Serial.println("Error al leer el sensor DHT11");
    return;
  }

  Serial.print("T: ");
  Serial.print(t);
  Serial.print(" *C | H: ");
  Serial.print(h);
  Serial.println(" %");
}