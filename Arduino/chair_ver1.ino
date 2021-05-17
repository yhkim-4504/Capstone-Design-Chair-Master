#include <Adafruit_NeoPixel.h>

/*

버전1: 압력센서 4개에 각각 LED를 대응해서 압력이 0이면 빨간색, 그 이상이면 초록색으로 빛나게 함.

*/

// 네오픽셀 개수, 핀 지정
#define PIN 3
Adafruit_NeoPixel strip = Adafruit_NeoPixel(4, PIN, NEO_GRB + NEO_KHZ800);



void setup() {

  // 네오픽셀 초기화
  strip.begin();
  strip.show();
    
  // 센서값 측정 위해 시리얼통신 준비
  Serial.begin(9600);
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);
  pinMode(A2, INPUT);
  pinMode(A3, INPUT);
  pinMode(3, OUTPUT);
}

void loop() {

  // 압력센서 4개
  int val_0 = analogRead(A0);
  int val_1 = analogRead(A1);
  int val_2 = analogRead(A2);
  int val_3 = analogRead(A3);
  
  // 입력이 0이면 빨간색, 그 이외에는 녹색으로 빛남
  if(analogRead(A0)==0) strip.setPixelColor(0, 255, 0, 0);
  else strip.setPixelColor(0, 0, 255, 0);
  if(analogRead(A1)==0) strip.setPixelColor(1, 255, 0, 0);
  else strip.setPixelColor(1, 0, 255, 0);
  if(analogRead(A2)==0) strip.setPixelColor(2, 255, 0, 0);
  else strip.setPixelColor(2, 0, 255, 0);
  if(analogRead(A3)==0) strip.setPixelColor(3, 255, 0, 0);
  else strip.setPixelColor(3, 0, 255, 0);

  strip.show();
  delay(100);
  
  //시리얼 모니터를 통해 센서값 표기 
  Serial.print(val_0);
  Serial.print(";");
  Serial.print(val_1);
  Serial.print(";");
  Serial.print(val_2);
  Serial.print(";");
  Serial.println(val_3);
}
