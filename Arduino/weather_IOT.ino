#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

const char* ssid = "test";
const char* password = "test";
const char* serverUrl = "http://192.168.1.100:5000/api/data";

#define DHTPIN D5
#define DHTTYPE DHT11
#define LUX_PIN A0

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  delay(2000)
  dht.begin();

  Serial.println("BOOT_OK");
  Serial.print("Connecting to WiFi");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWIFI_CONNECTED");
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
    Serial.println("WIFI_LOST");
    return;
  }

  WiFiClient client;
  HTTPClient http;

  http.begin(client, serverUrl);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<256> doc;
  doc["station_id"] = ESP.getChipId();
  doc["h"] = h;
  doc["t"] = t;
  doc["co2"] = co2;
  doc["o2"] = o2;
  doc["lux"] = lux;

  String payload;
  serializeJson(doc, payload);

  int httpCode = http.POST(payload);

  Serial.print("HTTP POST -> ");
  Serial.println(httpCode);

  http.end();
}