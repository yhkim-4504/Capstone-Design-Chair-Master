#include <Adafruit_NeoPixel.h>
// 포트 COM 5

#define PIN 3
Adafruit_NeoPixel strip = Adafruit_NeoPixel(10, PIN, NEO_GRB + NEO_KHZ800);


void setup() {
    strip.begin();
    strip.show();
}

void loop() {
  for(int i=0; i<10; i++) strip.setPixelColor(i, 255, 0, 0);
  strip.show();
  delay(500);
  for(int i=0; i<10; i++) strip.setPixelColor(i, 0, 255, 0);
  strip.show();
  delay(500);
  for(int i=0; i<10; i++) strip.setPixelColor(i, 0, 0, 255);
  strip.show();
  delay(500);
  for(int i=0; i<10; i++) strip.setPixelColor(i, 255, 255, 255);
  strip.show();
  delay(500);
}
