#include <WiFi.h>
#include <HTTPClient.h>
#include "time.h"
#include <Adafruit_BMP085.h>
#include <BH1750.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include "esp_sleep.h"
#include "esp_deep_sleep.h"

#define uS_TO_S_FACTOR 1000000ULL /* Conversion factor for micro seconds to seconds */
#define TIME_TO_SLEEP 900         /* Time ESP32 will go to sleep (in seconds) */
#define TIME_TO_RECONNECT  5
#define DEBOUNCE_DELAY 50
#define WIFI_TIMEOUT_MS 20000
#define WAKEUP_PIN GPIO_NUM_4

volatile unsigned long last_interrupt_time = 0;

#define DHTPIN 5
#define DHTTYPE DHT22
#define Hall_Wind 18
#define Hall_Rain 4

#define PULSE_COUNT_INDEX 0

#define PERIOD 5000         // Tempo de medida(miliseconds)
#define RADIUS 105          //  Aqui ajusta o raio do anemometro em milimetros  **************

DHT_Unified dht(DHTPIN, DHTTYPE);
Adafruit_BMP085 bmp;
BH1750 lightMeter(0x23);
// Constants definitions
const float pi = 3.14159265;  // Numero pi      
int delaytime = 2000;         // Time between samples (miliseconds)     
 
// Variable definitions
unsigned int Sample = 0;   // Sample number
unsigned int counter = 0;  // magnet counter for sensor
RTC_DATA_ATTR unsigned int REEDcount = 0;  // magnet counter for rain sensor
unsigned int RPM = 0;      // Revolutions per minute
float speedwind = 0;       // Wind speed (m/s)
float windspeed = 0;       // Wind speed (km/h)
//dir
int ar = 0;
int wd = 0;
int wds = 0;

struct BMP085data {
    float temperature;
    float pressure;
    float altitude;
};

struct DHT22data {
    float temperature;
    float humidity;
};

struct Winddata {
    float speed;
    uint16_t direction;
};

//const char* ssid = "lin-ufv";
//const char* password = "5y4X!6f%CrBs";

const char* ssid = "iPhone de Joicy";
const char* password = "Joicygbs2@2@";

const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 0;
const int   daylightOffset_sec = -3*3600;

void IRAM_ATTR addcount_wind();
void IRAM_ATTR addcount_rain();
uint16_t winddir();
float WindSpeed(int _radius, unsigned int _RPM);
float SpeedWind(int _radius, unsigned int _RPM);
unsigned int RPMcalc(unsigned int _counter);
void windvelocity();
void sendData(const String& payload);
float readBatt();

void printLocalTime() {
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) {
        Serial.println("Failed to obtain time");
        return;
    }
    Serial.println(&timeinfo, "%A, %B %d %Y %H:%M:%S");
}

void setup() {
    Serial.begin(115200);
    pinMode(Hall_Wind, INPUT);
    digitalWrite(Hall_Wind, HIGH);
    pinMode(Hall_Rain, INPUT);
    digitalWrite(Hall_Rain, HIGH);
    Wire.begin(22, 21);
    WiFi.begin(ssid, password);
    unsigned long startAttemptTime = millis();
    attachInterrupt(Hall_Rain, addcount_rain, RISING);

    esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();
    switch (wakeup_reason) {
        case ESP_SLEEP_WAKEUP_EXT0:
            //Serial.println("Wakeup caused by external signal using RTC_IO");
            REEDcount++;
            break;
        case ESP_SLEEP_WAKEUP_TIMER:
            //Serial.println("Wakeup caused by timer");
            break;
        default:
            //Serial.println("Wakeup was not caused by deep sleep");
            break;
    }

    // if (!bmp.begin()) {
    //     Serial.println("Could not find a valid BMP085 sensor, check wiring!");
    // }

    // if (!lightMeter.begin(BH1750::ONE_TIME_HIGH_RES_MODE)) {
    //     Serial.println(F("Error initialising BH1750"));
    // }
    //dht.begin();

    // Variable to store the MAC address
  uint8_t baseMac[6];
  
  // Get MAC address of the WiFi station interface
  // esp_read_mac(baseMac, ESP_MAC_WIFI_STA);
  // Serial.print("Station MAC: ");
  // for (int i = 0; i < 5; i++) {
  //   Serial.printf("%02X:", baseMac[i]);
  // }
  // Serial.printf("%02X\n", baseMac[5]);

    while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < WIFI_TIMEOUT_MS) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }

    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Failed to connect to WiFi. Going to sleep.");
        esp_sleep_enable_timer_wakeup(TIME_TO_RECONNECT * uS_TO_S_FACTOR);
        esp_deep_sleep_start();
    }
    
    Serial.println("Connected to WiFi");
    
    // Configurar o RTC com NTP
    configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
    //printLocalTime();
}

BMP085data readBMP085(){
    BMP085data data;
    //Serial.print("\nTemperature = ");
    data.temperature = bmp.readTemperature();
    //Serial.print(data.temperature);
    //Serial.println(" *C");

    //Serial.print("Pressure = ");
    data.pressure = (float)bmp.readPressure() / 100.0;
    //Serial.print(data.pressure);
    //Serial.println(" hPa");

    //Serial.print("Altitude = ");
    data.altitude = bmp.readAltitude(102290.0F);
    //Serial.print(data.altitude);
    //Serial.println(" meters");

    //Serial.print("Pressure at sealevel (calculated) = ");
    //Serial.print((float)bmp.readSealevelPressure() / 100.0);
    //Serial.println(" hPa");
    return data;
}

DHT22data readDHT22(){
    DHT22data data;
    sensors_event_t event;
  dht.temperature().getEvent(&event);
  if (isnan(event.temperature)) {
    Serial.println(F("Error reading temperature from DHT22!"));
  } else {
    //Serial.print(F("Temperature: "));
    data.temperature = event.temperature;
    //Serial.print(data.temperature);
    //Serial.println(F("°C"));
  }

  dht.humidity().getEvent(&event);
  if (isnan(event.relative_humidity)) {
    Serial.println(F("Error reading humidity from DHT22!"));
  } else {
    //Serial.print(F("Humidity: "));
    data.humidity = event.relative_humidity;
    //Serial.print(data.humidity);
    //Serial.println(F("%"));
  }
  return data;
}

Winddata readWindData(){
  float _windspeedms, _windspeedkh;
  uint16_t _winddir;
  Winddata data;
  windvelocity();
  //Serial.print("Counter: ");
  //Serial.print(counter);
  //Serial.print(";  RPM: ");
  RPM = RPMcalc(counter);
  //Serial.print(RPM);
  //Serial.print(";  Wind speed: ");
  //*****************************************************************
  //print m/s
  _windspeedms = WindSpeed(RADIUS, RPM);
  //Serial.print(_windspeedms);
  //Serial.print(" [m/s] ");
  //*****************************************************************
  //print km/h
  _windspeedkh = SpeedWind(RADIUS, RPM);
  //Serial.print(_windspeedkh);
  //Serial.print(" [km/h] ");
  //delay(delaytime);  //delay between prints
  //******************************
  //Direção
  _winddir = winddir();
  data.speed = _windspeedms;
  data.direction = _winddir;
  return data;

}

float readLuxData(){
    if (lightMeter.measurementReady(true)) {
    float lux = lightMeter.readLightLevel();
    //Serial.print(F("Light: "));
    //Serial.print(lux);
    //Serial.println(F(" lx"));

    if (lux < 0) {
      Serial.println(F("Error condition detected"));
    } else {
      if (lux > 40000.0) {
        // reduce measurement time - needed in direct sun light
        if (lightMeter.setMTreg(32)) {
          //Serial.println(
          //  F("Setting MTReg to low value for high light environment"));
        } else {
          Serial.println(
            F("Error setting MTReg to low value for high light environment"));
        }
      } else {
        if (lux > 10.0) {
          // typical light environment
          if (lightMeter.setMTreg(69)) {
            //Serial.println(F(
            //  "Setting MTReg to default value for normal light environment"));
          } else {
            Serial.println(F("Error setting MTReg to default value for normal "
                             "light environment"));
          }
        } else {
          if (lux <= 10.0) {
            // very low light environment
            if (lightMeter.setMTreg(138)) {
              //Serial.println(
              //  F("Setting MTReg to high value for low light environment"));
            } else {
              Serial.println(F("Error setting MTReg to high value for low "
                               "light environment"));
            }
          }
        }
      }
    }
    //Serial.println(F("--------------------------------------"));
    //Serial.flush();
    return lux;
  }
}

void loop() {
    if (WiFi.status() == WL_CONNECTED) {
        // Obter o timestamp atual
        struct tm timeinfo;
        if (!getLocalTime(&timeinfo)) {
            Serial.println("Failed to obtain time");
            return;
        }
        char timestamp[30];
        strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", &timeinfo);

        float rain_mm = REEDcount * 0.25;

        BMP085data dataBMP085 = readBMP085();  // Função descomentada para ler os dados
        // dataBMP085.altitude = 45.5;  // Removida a entrada manual
        // dataBMP085.pressure = 1019.0;  // Removida a entrada manual
        // dataBMP085.temperature = 30.0;  // Removida a entrada manual

        DHT22data dataDHT22 = readDHT22();  // Função descomentada para ler os dados
        // dataDHT22.humidity = 60;  // Removida a entrada manual
        // dataDHT22.temperature = 29.2;  // Removida a entrada manual

        Winddata dataWind = readWindData();  // Função descomentada para ler os dados
        // dataWind.direction = 0;  // Removida a entrada manual
        // dataWind.speed = 3.56;  // Removida a entrada manual

        float lux = readLuxData();  // Função descomentada para ler os dados
        // lux = 15653.12;  // Removida a entrada manual
 
        float battery_voltage = readBatt();  // ok
      
        //Serial.print(F("Rain fall: "));
        //Serial.print(rain_mm);
        //Serial.println(F("mm"));
        //HTTPClient http;
        //http.begin("https://0b74-200-137-83-157.ngrok-free.app/data"); // Substitua "your_server_ip" pelo IP do servidor Flask
        //http.addHeader("Content-Type", "application/json");

        // Formatar o payload JSON com todos os dados
        String payload = String("{\"temperature\":") + dataBMP085.temperature +
                         ", \"pressure\":" + dataBMP085.pressure +
                         ", \"humidity\":" + dataDHT22.humidity +
                         ", \"altitude\":" + dataBMP085.altitude +
                         ", \"rainfall\":" + rain_mm +
                         ", \"wind_speed\":" + dataWind.speed +
                         ", \"wind_direction\":\"" + dataWind.direction + "\"" +
                         ", \"lux\":" + lux +
                         ", \"battery_voltage\":" + battery_voltage +
                         ", \"timestamp\":\"" + timestamp + "\"}";

        sendData(payload);   
        esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
        esp_sleep_enable_ext0_wakeup(WAKEUP_PIN, 1);
        esp_deep_sleep_start();
    }
}

void IRAM_ATTR addcount_wind() {
  counter++;
}

void IRAM_ATTR addcount_rain() {
  unsigned long interrupt_time = millis();
    if (interrupt_time - last_interrupt_time > DEBOUNCE_DELAY) {
        REEDcount++;
        last_interrupt_time = interrupt_time;
    }
}

// Measure wind speed
void windvelocity() {
  speedwind = 0;
  windspeed = 0;
  counter = 0;
  attachInterrupt(Hall_Wind, addcount_wind, RISING);
  unsigned long millis();
  long startTime = millis();
  while (millis() < startTime + PERIOD) {
  }
}

unsigned int RPMcalc(unsigned int _counter) {
  return ((_counter)*60) / (PERIOD / 1000);  // Calculate revolutions per minute (RPM)
}

float WindSpeed(int _radius, unsigned int _RPM) {
  return ((4 * pi * _radius * _RPM) / 60) / 1000;  // Calculate wind speed on m/s
}

float SpeedWind(int _radius, unsigned int _RPM) {
  return (((4 * pi * _radius * _RPM) / 60) / 1000) * 3.6;  // Calculate wind speed on km/h
}

uint16_t winddir() {
  for (int i = 0; i < 20; i++) {
    wd = analogRead(34);  //34 esp ou  A0 arduino
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
  if (ar >= 65 && ar <= 82) {
    wdir = 270;
  }
  if (ar >= 83 && ar <= 207) {
    wdir = 225;
  }
  if (ar >= 208 && ar <= 337) {
    wdir = 180;
  }
  if (ar >= 338 && ar <= 463) {
    wdir = 135;
  }
  if (ar >= 464 && ar <= 590) {
    wdir = 90;
  }
  if (ar >= 591 && ar <= 718) {
    wdir = 45;
  }
  if (ar >= 719) {
    wdir = 0;
  }
  //Serial.print("Leitura  Analog Media : ");
  //Serial.print(ar);
  //Serial.print(" - Direção : ");
  //Serial.println(wdir);
  ar = 0;
  wd = 0;
  wds = 0;
  return wdir;
}

float readBatt() {
  int Vbattadc = 0;
  int Vbattadd = 0;  
  for (int i = 0; i < 5; i++) {
    Vbattadc = analogRead(35);  // analog pin 35
    Vbattadd = Vbattadd + Vbattadc;
    delay(20);
  }
  Vbattadc = Vbattadd / 5;
  return ((3.30F/4095.0F)*Vbattadc)*(1.24666F);
}

void sendData(const String& payload) {
    HTTPClient http;
    http.begin("http://619d-200-137-83-157.ngrok-free.app/data"); // Substitua com o seu URL
    //http.begin("http://200.137.83.155:5003/data");
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode;
    int retries = 0;
    const int maxRetries = 5; // Número máximo de tentativas

    do {
        httpResponseCode = http.POST(payload);

        if (httpResponseCode > 0) {
            if (httpResponseCode == 200) {
                String response = http.getString();
                //Serial.print("HTTP Response code: ");
                //Serial.println(httpResponseCode);
                //Serial.print("Response: ");
                //Serial.println(response);
                break; // Saída bem-sucedida do loop
            } else if (httpResponseCode >= 500) {
                Serial.print("HTTP Response code: ");
                Serial.println(httpResponseCode);
                Serial.println("Retrying...");
            } else{
                Serial.print("Error on sending POST: ");
                Serial.println(httpResponseCode);
                break;
            }
        } else {
            Serial.print("Error on sending POST: ");
            Serial.println(httpResponseCode);
        }

        retries++;
        delay(2000); // Atraso de 2000 ms antes da próxima tentativa
    } while (retries < maxRetries);

    if (retries == maxRetries) {
        Serial.println("Failed to send POST after retries");
    }

    http.end(); // Encerra a conexão
}
