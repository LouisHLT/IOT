#include <Arduino.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* ssid = "iPhoneee";
const char* password = "iot12345%";
const char* server = "http://172.20.10.2:5000/data";
//const char* server = "http://192.168.1.255:5000/data";


#define DHTPIN D5
#define DHTTYPE DHT11
#define LUX_PIN A0

DHT dht(DHTPIN, DHTTYPE);
void setup() {
  Serial.begin(9600);
  delay(1000);

  Serial.println();
  Serial.println("BOOT");

  dht.begin();

  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);

  Serial.println("\nScanning networks...");
  int n = WiFi.scanNetworks();
  Serial.println("Scan done");
  
  if (n == 0) {
    Serial.println("No networks found");
  } else {
    for (int i = 0; i < n; i++) {
      Serial.println(WiFi.SSID(i));
    }
  }

  int tries = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    tries++;
    if (tries > 2000) {
      Serial.println("\nWiFi FAILED");
      return;
    }
  }

  Serial.println("\nWiFi CONNECTED");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}


void loop() {
  //Read sensors
  float h = dht.readHumidity();
  float t = dht.readTemperature(); // Celsius
  int luxRaw = analogRead(LUX_PIN);     // 0–1023

  if (isnan(h) || isnan(t)) {
    Serial.println("DHT_ERROR");
    delay(2000);
    return;
  }

  //Map LDR to percentage (0–100)
  float lux = map(luxRaw, 0, 1023, 0, 100);

  // Simulated o2/co2
  float co2 = random(400, 3000);
  float o2  = random(180, 220) / 10.0;

  sendData(h, t, co2, o2, lux);
  Serial.println();
  delay(2000);
}

void sendData(float h, float t, float co2, float o2, float lux) {

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi LOST");
    return;
  }

  WiFiClient client;
  HTTPClient http;

  StaticJsonDocument<256> doc;
  doc["station_id"] = ESP.getChipId();
  doc["h"] = h;
  doc["t"] = t;
  doc["co2"] = co2;
  doc["o2"] = o2;
  doc["lux"] = lux;

  String payload;
  serializeJson(doc, payload);

  Serial.println("Sending:");
  Serial.println(payload);

  http.begin(client, server);
  http.addHeader("Content-Type", "application/json");

  int code = http.POST(payload);

  Serial.print("HTTP code: ");
  Serial.println(code);

  http.end();
}
