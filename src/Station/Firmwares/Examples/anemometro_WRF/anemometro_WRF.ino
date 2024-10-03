// Pin definitions
#define Hall sensor 2  //  Pino digital 2
// Constants definitions
const float pi = 3.14159265;  // Numero pi
int period = 5000;            // T empo de medida(miliseconds)
int delaytime = 2000;         // Time between samples (miliseconds)
int radius = 105;             //  Aqui ajusta o raio do anemometro em milimetros  **************
// V ariable definitions
unsigned int Sample = 0;   // Sample number
unsigned int counter = 0;  // magnet counter for sensor
unsigned int RPM = 0;      // Revolutions per minute
float speedwind = 0;       // Wind speed (m/s)
float windspeed = 0;       // Wind speed (km/h)
//dir
int ar = 0;
int wd = 0;
int wds = 0;
void setup() {
  // Set the pins
  pinMode(2, INPUT);
  digitalWrite(2, HIGH);  //internall pull-up active
  //Start serial
  Serial.begin(9600);  // sets the serial port to 9600 baud
}
void loop() {
  Sample++;
  Serial.print(Sample);
  Serial.print(": Start measurement...");
  windvelocity();
  Serial.println("   finished.");
  Serial.print("Counter: ");
  Serial.print(counter);
  Serial.print(";  RPM: ");
  RPMcalc();
  Serial.print(RPM);
  Serial.print(";  Wind speed: ");
  //*****************************************************************
  //print m/s
  WindSpeed();
  Serial.print(windspeed);
  Serial.print(" [m/s] ");
  //*****************************************************************
  //print km/h
  SpeedWind();
  Serial.print(speedwind);
  Serial.print(" [km/h] ");
  Serial.println();
  delay(delaytime);  //delay between prints
  //******************************
  //Direção
  winddir();
}
// Measure wind speed
void windvelocity() {
  speedwind = 0;
  windspeed = 0;
  counter = 0;
  attachInterrupt(0, addcount, RISING);
  unsigned long millis();
  long startTime = millis();
  while (millis() < startTime + period) {
  }
}
void RPMcalc() {
  RPM = ((counter)*60) / (period / 1000);  // Calculate revolutions per minute (RPM)
}
void WindSpeed() {
  windspeed = ((4 * pi * radius * RPM) / 60) / 1000;  // Calculate wind speed on m/s
}
void SpeedWind() {
  speedwind = (((4 * pi * radius * RPM) / 60) / 1000) * 3.6;  // Calculate wind speed on km/h
}
void addcount() {
  counter++;
}
void winddir() {
  for (int i = 0; i < 20; i++) {
    wd = analogRead(0);  //34 esp ou  A0 arduino
    Serial.println(wd);
    wds = wds + wd;
    delay(50);
  }
  ar = wds / 20;
  int wdir;
  if (ar >= 0 && ar <= 64) {
    wdir = 315;
  }
  if (ar >= 65 && ar <= 100) {
    wdir = 270;
  }
  if (ar >= 101 && ar <= 200) {
    wdir = 225;
  }
  if (ar >= 201 && ar <= 300) {
    wdir = 180;
  }
  if (ar >= 301 && ar <= 400) {
    wdir = 135;
  }
  if (ar >= 401 && ar <= 480) {
    wdir = 90;
  }
  if (ar >= 481 && ar <= 580) {
    wdir = 45;
  }
  if (ar >= 581 && ar <= 699) {
    wdir = 0;
  }
  Serial.print("Leitura  Analog Media : ");
  Serial.print(ar);
  Serial.print(" - Direção : ");
  Serial.println(wdir);
  delay(1000);
  ar = 0;
  wd = 0;
  wds = 0;
}
