#include <DHT.h>
#define DHTPIN 2
#define DHTTYPE DHT11
#include <SoftwareSerial.h>
#include "NewPing.h"
#include <Servo.h>

SoftwareSerial mySerial(10, 11); // RX, TX 

DHT dht(DHTPIN, DHTTYPE);

unsigned long timeout= 5000;
unsigned long timerEnvio=0;
unsigned long periodoHT=1000;
unsigned long timerht=0;
bool enviarht = true;
bool error = false;
volatile int angulo=0;
bool enviarDistancia = true;
unsigned long periododist=40;
int fallosDist1=0;
int fallosDist2=0;
unsigned long ultimoEco1=0;
unsigned long ultimoEco2=0;
unsigned long timerErroresDist = 0;

bool modoSatelite = false;
float ultimasTemp[10]; //(el array de las 10 últimas temperaturas)

int indiceTemp = 0; //la posición actual del array, con otro nombre para no chocar con el byte indice
int numMuestras = 0; //(cuántas muestras llevamos guardadas hasta llegar a 10).
float mediaTemp = 0.0; //(el resultado de la media).
int consecutivosSat = 0; //(contador de superaciones seguidas).
float limiteSatelite = 28.0; //limite de temperatura 


// Variables del sensor de temperatura / humedad
float h;
float t;

// Definir Pins del sensor de ultrasonidos y la distancia maxima
#define trigPin1 4
#define echoPin1 3
#define MAX_DISTANCE 350 //Distancia maxima que queremos medir (el maximo del sensor es 400-500cm)



Servo servoMotor;

// Pines Sensor 1 (Frontal: 0° a 180°)
#define trigPin1 4
#define echoPin1 3

// Pines Sensor 2 (Trasero: 180° a 360°)
#define trigPin2 5
#define echoPin2 6

#define MAX_DISTANCE 350
NewPing sonar1(trigPin1, echoPin1, MAX_DISTANCE);
NewPing sonar2(trigPin2, echoPin2, MAX_DISTANCE);

unsigned long int timerDistancia = 0;
int dist1 = 0;
int dist2 = 0;
bool turnoSensor1 = true;

void ActualizarDistancias() {

  if (!enviarDistancia) {
    dist1 = 0;
    dist2 = 0;
    return;
  }

  if (millis() >= timerDistancia) {

    timerDistancia = millis() + periododist;

  if (turnoSensor1) {
    dist1 = sonar1.ping_cm();
  }
  else {
    dist2 = sonar2.ping_cm();
  }

  turnoSensor1 = !turnoSensor1;
  }
}

// Recepcion 2, para probar solamente porque Recepcion normal ya funciona bien.
char buffer[20];
byte indice = 0;

bool esNumero(String str) {
  if (str.length() == 0) return false;
  for (unsigned int i = 0; i < str.length(); i++) {
    if (!isDigit(str.charAt(i))) return false;
  }
  return true;
}

void moverServo(){
  servoMotor.write(angulo);
  mySerial.println(angulo);
}

void Recepcion() {
  if (mySerial.available() > 0) {

    String orden = mySerial.readStringUntil('\n');
    orden.trim();

    int separador = orden.indexOf(':');

    if (separador == -1) {
      mySerial.println("Formato invalido");
      return;
    }

    String comando = orden.substring(0, separador);
    String valor = orden.substring(separador + 1);

    // Protocolo 1 -> Temperatura y humedad
    if (comando == "1") {

      if (valor == "0") {
        enviarht = false;
        mySerial.println("HT detenido");
      }
      else if (valor == "1") {
        enviarht = true;
        mySerial.println("HT reanudado");
      }
      else {
        mySerial.println("Valor invalido");
      }

    }

    // Protocolo 2 -> Servo
    else if (comando == "2") {

      if (esNumero(valor)) {

        int nuevoAngulo = valor.toInt();

        if (nuevoAngulo >= 0 && nuevoAngulo <= 180) {
          angulo = nuevoAngulo;
          moverServo();

          mySerial.print("Servo=");
          mySerial.println(angulo);
        }
        else {
          mySerial.println("Angulo fuera de rango");
        }

      }
      else {
        mySerial.println("Angulo invalido");
      }

    }

    // Protocolo 3 -> Distancia
    else if (comando == "3") {

      if (valor == "0") {
        enviarDistancia = false;
        mySerial.println("Distancia detenida");
      }
      else if (valor == "1") {
        enviarDistancia = true;
        mySerial.println("Distancia reanudada");
      }
      else {
        mySerial.println("Valor invalido");
      }

    }
    else if (comando == "4") {
      if (esNumero(valor)) {

        unsigned long nuevoPeriodo = valor.toInt();

        // Limites de seguridad
        if (nuevoPeriodo >= 100 && nuevoPeriodo <= 60000) {

          periodoHT = nuevoPeriodo;

          mySerial.print("Periodo HT=");
          mySerial.print(periodoHT);
          mySerial.println(" ms");
        }
        else {
          mySerial.println("Periodo fuera de rango");
        }
      }
      else {
        mySerial.println("Periodo invalido");
      }
    }
    else if(comando=="5"){
      if (esNumero(valor)) {

        unsigned long nuevoPeriodo = valor.toInt();

        // Limites de seguridad
        if (nuevoPeriodo >= 10 && nuevoPeriodo <= 60000) {

          periododist = nuevoPeriodo;

          mySerial.print("Periodo Dist=");
          mySerial.print(periododist);
          mySerial.println(" ms");
        }
        else {
          mySerial.println("Periodo fuera de rango");
        }
      }
      else {
        mySerial.println("Periodo invalido");
      }
    }
    else if (comando=="6"){
      if (valor=="0"){
        mySerial.println("Modo Tierra");
        modoSatelite=false;
        mySerial.println("RECIBIDO MODO_TIERRA");
        // Resetear los datos necesarios para calcular la media.
        numMuestras = 0;
        indiceTemp = 0;
        consecutivosSat = 0;
        mediaTemp = 0;
        for(int i=0;i<10;i++){
          ultimasTemp[i]=0;
        }
      }
      else if (valor=="1"){
        mySerial.println("Modo Satelite");
        numMuestras = 0;
        indiceTemp = 0;
        consecutivosSat = 0;
        mediaTemp = 0;

        for(int i=0;i<10;i++){
            ultimasTemp[i]=0;
        }
        modoSatelite=true;
        mySerial.println("RECIBIDO MODO_SATELITE");
      }
    }
    else if (comando=="7"){
        limiteSatelite=valor.toFloat();
    }
    else {
      mySerial.println("Comando desconocido");
    }
  }
}

void calc_media(){
  if (modoSatelite==true){
    ultimasTemp[indiceTemp] = t;
    indiceTemp = (indiceTemp + 1) % 10;
    if (numMuestras < 10) {
      numMuestras++;
    }
    // 2. Sumamos las muestras guardadas y dividimos para sacar la media
    float suma = 0;
    for (int k = 0; k < numMuestras; k++) {
          suma += ultimasTemp[k];
      }

      if (numMuestras > 0) {
          mediaTemp = suma / numMuestras;
      }
      // 3.Comprobamos la alarma inmediata (3 consecutivas > límite)
      if (mediaTemp > limiteSatelite) {
        consecutivosSat++;
        if (consecutivosSat >= 3) {
        }
      } 
      else {
        consecutivosSat = 0;      
      }
  }
  else {
    mediaTemp=0;
  }
}

void Transmision() {
  ActualizarDistancias();

  if (enviarht) {
    if (millis() >= timerht) {
      t = dht.readTemperature();
      h = dht.readHumidity();
      timerht=millis()+periodoHT;
      if (isnan(t) || isnan(h)) {
        if (!error) {
          error = true;
          timeout = millis() + 5000;
        }
        if (millis() >= timeout) {
          mySerial.print("error:");
          mySerial.println("1");
          timeout=millis()+5000;
        }
        return;
      }
      error = false;
    }
  } else {
    t = 0;
    h = 0;
  }
  if (millis() >= timerErroresDist) {

      timerErroresDist = millis() + 1000;

      if (dist1 > 0) {
          fallosDist1 = 0;
          ultimoEco1 = millis();
      }
      else {
          fallosDist1++;
      }

      if (dist2 > 0) {
          fallosDist2 = 0;
          ultimoEco2 = millis();
      }
      else {
          fallosDist2++;
      }

      if (fallosDist1 > 20 && millis() - ultimoEco1 > 5000) {
          mySerial.println("error:31");
      }
      if (fallosDist2 > 20 && millis() - ultimoEco2 > 5000){
        mySerial.println("error:32");
      }
  }

  if (millis() >= timerEnvio && error==false) {
    calc_media();
    mySerial.print(1); // Heartbeat
    mySerial.print(":T:");
    mySerial.print(t);
    mySerial.print(":H:");
    mySerial.print(h);
    mySerial.print(":D1:");
    mySerial.print(dist1);
    mySerial.print(":D2:");
    mySerial.print(dist2);
    mySerial.print(":M:");
    mySerial.println(mediaTemp);

    timerEnvio = millis() + 1000;
  }
}

void setup() {
  // Inicializar puertos Serial y mySerial y sensores
  Serial.begin(9600);
  dht.begin();
  mySerial.begin(9600);
  // Inicializacion de los pines del sensor de ultrasonido. No hacen falta pero tampoco sobran.
  pinMode(trigPin1, OUTPUT); 
  pinMode(echoPin1, INPUT);
  pinMode(trigPin2, OUTPUT); 
  pinMode(echoPin2, INPUT);

  // Motor del sensor de ultrasonido
  servoMotor.attach(7);
  servoMotor.write(angulo);
}

void loop() {
  Recepcion(); // Cambiar por Recepcion 2 despues a ver si funciona
  Transmision();
  
}

