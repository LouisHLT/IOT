#include <Arduino.h>
#include <DHT.h>



#define O2 A0


void setup() {
  Serial.begin(9600);
  delay(2000);

}

void loop() {

  int o2 = analogRead(O2);     // 0–1023
  

  Serial.println(o2);
  delay(2000);
}
