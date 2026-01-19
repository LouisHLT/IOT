// Import required libraries
#include <ESP8266WiFi.h>
#include <ESPAsyncWebServer.h>
#include <Arduino.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

const char* ssid = "iPhoneee";
const char* password = "iot12345%";
const char* serverUrl = "http://192.168.1.100:5000/data";

AsyncWebServer server(80);

#define DHTPIN D5
#define DHTTYPE DHT11
#define LUX_PIN A0
DHT dht(DHTPIN, DHTTYPE);


void setup() {
  Serial.begin(9600);
  delay(2000);
  dht.begin();

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

  Serial.print("Setting AP (Access Point)…");
  Serial.println();
  WiFi.softAP(ssid, password);

  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);

  server.on("/", handle_onConnect);
  server.onNotFound(handle_NotFound);

  server.begin();           // Start Server
  Serial.println("HTTP server started");
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

void handle_onConnect() {
  //Read DHT Sensor & LDR
  float h = dht.readHumidity();
  float t = dht.readTemperature(); // in celsius
  int luxRaw = analogRead(LUX_PIN); // default value is [0-1023]
  
  if (isnan(h) || isnan(t)) {
    Serial.println("DHT_ERROR");
    server.send(500, "text/plain", "Sensor error");
    return;
  }
  
  float lux = map(luxRaw, 0, 1023, 0, 100);
  
  // Simulated o2/co2 values
  float co2 = random(400, 3000);
  float o2  = random(180, 220) / 10.0;

  server.send(200, "text/html", SendHTML(h, t, co2, o2, lux));
}

void handle_NotFound(){
  server.send(404, "text/plain", "Not found");
}

String SendHTML(float humidity, float temperature, float co2, float o2, float lux){
  String ptr = "<!DOCTYPE html> <html>\n";
  ptr +="<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0, user-scalable=no\">\n";
  ptr +="<title>ESP8266 Weather Station</title>\n";
  ptr +="<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}\n";
  ptr +="body{margin-top: 50px;} h1 {color: #444444;margin: 50px auto 30px;}\n";
  ptr +="p {font-size: 24px;color: #444444;margin-bottom: 10px;}\n";
  ptr +="</style>\n";
  ptr +="</head>\n";
  ptr +="<body>\n";
  ptr +="<div id=\"webpage\">\n";
  ptr +="<h1>ESP8266 Weather Station</h1>\n";
  ptr +="<p>Temperature: ";
  ptr +=temperature;
  ptr +="&deg;C</p>";
  ptr +="<p>Humidity: ";
  ptr +=humidity;
  ptr +="%</p>";
  ptr +="<p>CO2: ";
  ptr +=co2;
  ptr +=" ppm</p>";
  ptr +="<p>O2: ";
  ptr +=o2;
  ptr +="%</p>";
  ptr +="<p>Light: ";
  ptr +=lux;
  ptr +="%</p>";
  ptr +="</div>\n";
  ptr +="</body>\n";
  ptr +="</html>\n";
  return ptr;
}

void sendData(float h, float t, float co2, float o2, float lux) {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    
    http.begin(client, serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    StaticJsonDocument<200> doc;
    doc["station_id"] = "ESP_001";
    doc["t"] = t;
    doc["h"] = h;
    doc["co2"] = co2;
    doc["o2"] = o2;
    doc["lux"] = lux;
    
    String jsonString;
    serializeJson(doc, jsonString);
    
    int httpCode = http.POST(jsonString);
    
    if (httpCode > 0) {
      Serial.print("HTTP Response: ");
      Serial.println(httpCode);
      String payload = http.getString();
      Serial.println(payload);
    } else {
      Serial.print("HTTP Error: ");
      Serial.println(http.errorToString(httpCode));
    }
    
    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
}