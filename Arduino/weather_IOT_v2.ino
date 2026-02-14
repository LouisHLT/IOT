#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

const char* ssid     = "ADB-F20AC1";
const char* password = "yxhf6p2wnmkd9gtj";

const char* SERVER_URL = "http://192.168.1.11:5050/ingest";

#define DHTPIN D5
#define DHTTYPE DHT11
#define LUX_PIN A0
#define PUSH_INTERVAL 1000   // ms between pushes

DHT dht(DHTPIN, DHTTYPE);
WiFiClient wifiClient;

void setup() {
  Serial.begin(115200);
  dht.begin();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected: " + WiFi.localIP().toString());
}

void loop() {
  float h      = dht.readHumidity();
  float t      = dht.readTemperature();
  int luxRaw   = analogRead(LUX_PIN);

  if (isnan(h) || isnan(t)) {
    Serial.println("DHT read failed");
    delay(PUSH_INTERVAL);
    return;
  }

  float lux = (luxRaw / 1023.0) * 100.0;
  float co2 = random(400, 3000);
  float o2  = random(180, 220) / 10.0;

  StaticJsonDocument<200> doc;
  doc["id"]  = "esp8266_room1";   // ← unique per device
  doc["t"]   = t;
  doc["h"]   = h;
  doc["co2"] = co2;
  doc["o2"]  = o2;
  doc["lux"] = lux;

  String body;
  serializeJson(doc, body);

  HTTPClient http;
  http.begin(wifiClient, SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  int code = http.POST(body);
  if (code > 0) {
    Serial.printf("POST %d\n", code);
  } else {
    Serial.printf("POST failed: %s\n", http.errorToString(code).c_str());
  }
  http.end();

  delay(PUSH_INTERVAL);
}