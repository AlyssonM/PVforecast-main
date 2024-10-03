#include <Adafruit_BMP085.h>
#include <BH1750.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

#define uS_TO_S_FACTOR 1000000ULL /* Conversion factor for micro seconds to seconds */
#define TIME_TO_SLEEP1 54         /* Time ESP32 will go to sleep (in seconds) */
#define TIME_TO_SLEEP2 30         /* Time ESP32 will go to sleep (in seconds) */

// Pinos I2C dos sensores de pressão e irradiância
// SDA = D22
// SCL = D21
#define DHTPIN 5       // DHT22 - D5
#define DHTTYPE DHT22  
#define Hall sensor 4  // Anemômetro - D4

DHT_Unified dht(DHTPIN, DHTTYPE);
Adafruit_BMP085 bmp;
BH1750 lightMeter(0x23);
RTC_DATA_ATTR float lux = 0;
// Constants definitions
const float pi = 3.14159265;  // Numero pi
int period = 5000;            // Tempo de medida(miliseconds)
int delaytime = 2000;         // Time between samples (miliseconds)
int radius = 105;             //  Aqui ajusta o raio do anemometro em milimetros  **************
// Variable definitions
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
  Serial.begin(9600);
  pinMode(4, INPUT);
  digitalWrite(4, HIGH);
  Wire.begin();
  if (!bmp.begin()) {
    Serial.println("Could not find a valid BMP085 sensor, check wiring!");
  }

  if (!lightMeter.begin(BH1750::ONE_TIME_HIGH_RES_MODE)) {
    Serial.println(F("Error initialising BH1750"));
  }
   dht.begin();
}

void loop() {
  Serial.print("\nTemperature = ");
  Serial.print(bmp.readTemperature());
  Serial.println(" *C");

  Serial.print("Pressure = ");
  Serial.print((float)bmp.readPressure() / 100.0);
  Serial.println(" hPa");

  Serial.print("Altitude = ");
  Serial.print(bmp.readAltitude());
  Serial.println(" meters");

  Serial.print("Pressure at sealevel (calculated) = ");
  Serial.print((float)bmp.readSealevelPressure() / 100.0);
  Serial.println(" hPa");

  Serial.print("Real altitude = ");
  Serial.print(bmp.readAltitude(101500));
  Serial.println(" meters");
  
  sensors_event_t event;
  dht.temperature().getEvent(&event);
  if (isnan(event.temperature)) {
    Serial.println(F("Error reading temperature from DHT22!"));
  } else {
    Serial.print(F("Temperature: "));
    Serial.print(event.temperature);
    Serial.println(F("°C"));
  }

  dht.humidity().getEvent(&event);
  if (isnan(event.relative_humidity)) {
    Serial.println(F("Error reading humidity from DHT22!"));
  } else {
    Serial.print(F("Humidity: "));
    Serial.print(event.relative_humidity);
    Serial.println(F("%"));
  }

  windvelocity();
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
  //delay(delaytime);  //delay between prints
  //******************************
  //Direção
  winddir();

  if (lightMeter.measurementReady(true)) {
    lux = lightMeter.readLightLevel();
    Serial.print(F("Light: "));
    Serial.print(lux);
    Serial.println(F(" lx"));

    if (lux < 0) {
      Serial.println(F("Error condition detected"));
    } else {
      if (lux > 40000.0) {
        // reduce measurement time - needed in direct sun light
        if (lightMeter.setMTreg(32)) {
          Serial.println(
            F("Setting MTReg to low value for high light environment"));
        } else {
          Serial.println(
            F("Error setting MTReg to low value for high light environment"));
        }
      } else {
        if (lux > 10.0) {
          // typical light environment
          if (lightMeter.setMTreg(69)) {
            Serial.println(F(
              "Setting MTReg to default value for normal light environment"));
          } else {
            Serial.println(F("Error setting MTReg to default value for normal "
                             "light environment"));
          }
        } else {
          if (lux <= 10.0) {
            // very low light environment
            if (lightMeter.setMTreg(138)) {
              Serial.println(
                F("Setting MTReg to high value for low light environment"));
            } else {
              Serial.println(F("Error setting MTReg to high value for low "
                               "light environment"));
            }
          }
        }
      }
    }
    Serial.println(F("--------------------------------------"));
    Serial.flush();
    esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP1 * uS_TO_S_FACTOR);
    esp_deep_sleep_start();
  }
}

void IRAM_ATTR addcount() {
  counter++;
}
// Measure wind speed
void windvelocity() {
  speedwind = 0;
  windspeed = 0;
  counter = 0;
  attachInterrupt(4, addcount, RISING);
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
void winddir() {
  for (int i = 0; i < 20; i++) {
    wd = analogRead(15);  //34 esp ou  A0 arduino
    wd = map(wd, 0, 4095, 0, 1023);
    //Serial.println(wd);
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
  //delay(1000);
  ar = 0;
  wd = 0;
  wds = 0;
}
