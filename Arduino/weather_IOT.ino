// Import required libraries
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <Arduino.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>


const char* ssid = "ADB-F20AC1";
const char* password = "yxhf6p2wnmkd9gtj";

ESP8266WebServer server(80);

#define DHTPIN D5
#define DHTTYPE DHT11
#define LUX_PIN A0
DHT dht(DHTPIN, DHTTYPE);


void handle_api() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  int luxRaw = analogRead(LUX_PIN);

  if (isnan(h) || isnan(t)) {
    server.send(500, "application/json", "{\"error\":\"sensor\"}");
    return;
  }

  float lux = (luxRaw / 1023.0) * 100.0;
  float co2 = random(400, 3000);
  float o2  = random(180, 220) / 10.0;

  StaticJsonDocument<200> doc;
  doc["id"] = "esp8266_room1";
  doc["t"] = t;
  doc["h"] = h;
  doc["co2"] = co2;
  doc["o2"] = o2;
  doc["lux"] = lux;

  String json;
  serializeJson(doc, json);
  server.send(200, "application/json", json);
}

void handle_onConnect() {
  //Read DHT Sensor & LDR
  float h = dht.readHumidity();
  float t = dht.readTemperature(); // in celsius
  int luxRaw = analogRead(LUX_PIN); // default value is [0-1023]
  if (isnan(h) || isnan(t)) {
    Serial.println("DHT_ERROR");
    delay(2000);
    return;
  }
  float lux = (luxRaw / 1023.0) * 100.0;
  
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


void setup() {
  Serial.begin(115200);
  //delay(2000);
  delay(100);
  dht.begin();

  Serial.println("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while(WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected!");
  Serial.print("Got IP: ");
  Serial.println(WiFi.localIP());

  server.on("/", handle_onConnect);
  server.on("/api", handle_api);
  server.onNotFound(handle_NotFound);

  server.begin();
  Serial.println("HTTP sever started");
}

void loop() {
  server.handleClient();
}