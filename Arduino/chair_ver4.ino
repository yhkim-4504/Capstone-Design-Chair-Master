#include <Adafruit_NeoPixel.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

/*

버전3: 압력센서 4개 + 초음파센서 + LCD + 버튼 통합

*/

// 0x3F I2C 주소를 가지고 있는 16x2 LCD객체를 생성합니다.(I2C 주소는 LCD에 맞게 수정해야 합니다.)
LiquidCrystal_I2C lcd(0x27, 16, 2);


#define PIN   3     // 네오픽셀 개수, 핀 지정
#define TRIG  9     // TRIG 핀 설정 (초음파 보내는 핀)
#define ECHO  8     // ECHO 핀 설정 (초음파 받는 핀)
Adafruit_NeoPixel strip = Adafruit_NeoPixel(5, PIN, NEO_GRB + NEO_KHZ800);

int MAX = 0;
int RAN = 0;

void setup() {

  // LCD 초기화
  lcd.init();
  lcd.backlight();

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
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  pinMode(5, INPUT_PULLUP);
  pinMode(6, INPUT_PULLUP);
  pinMode(7, INPUT_PULLUP);
}

void loop() {

  long duration, distance;
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  duration = pulseIn (ECHO, HIGH);  // 물체에 반사되어 돌아온 초음파의 시간을 변수에 저장
  distance = duration * 17 / 1000;  // 거리 계산

  // 압력센서 4개 + 초음파센서 거리
  int val_0 = analogRead(A0);
  int val_1 = analogRead(A1);
  int val_2 = analogRead(A2);
  int val_3 = analogRead(A3);
  int val_4 = distance;

  // 압력센서 최대값 계산
  MAX = 1;
  if(val_0 <= val_1) MAX = 2;
  if(MAX <= val_2) MAX = 3;
  if(MAX <= val_3) MAX = 4;

  // 불균형도 계산
  int temp = val_0 + val_1 + val_2 + val_3;
  RAN = temp / 25;
  
  // 입력이 0이면 빨간색, 그 이외에는 녹색으로 빛남
  if(analogRead(A0)<=20) strip.setPixelColor(0, 200, 0, 0);
  else strip.setPixelColor(0, 0, 200, 0);
  if(analogRead(A1)<=20) strip.setPixelColor(1, 200, 0, 0);
  else strip.setPixelColor(1, 0, 200, 0);
  if(analogRead(A2)<=20) strip.setPixelColor(2, 200, 0, 0);
  else strip.setPixelColor(2, 0, 200, 0);
  if(analogRead(A3)<=20) strip.setPixelColor(3, 200, 0, 0);
  else strip.setPixelColor(3, 0, 200, 0);
  if(distance>=10) strip.setPixelColor(4, 200, 0, 0);
  else strip.setPixelColor(4, 0, 200, 0);

  strip.show();
  delay(100);
  
  //시리얼 모니터를 통해 센서값 표기 
  Serial.print(val_0);
  Serial.print(";");
  Serial.print(val_1);
  Serial.print(";");
  Serial.print(val_2);
  Serial.print(";");
  Serial.print(val_3);
  Serial.print(";");
  Serial.println(val_4);

  lcd.setCursor(0,0);           // 0번째 줄 0번째 셀부터 입력하게 합니다.
  lcd.print("    CAPSTONE    ");  // 문구를 출력합니다.
  lcd.setCursor(0,1);           // 1번째 줄 0번째 셀부터 입력하게 합니다.
  lcd.print("     MUYAHO     ");

  // 1번 버튼 누르면 가장 값이 큰 압력센서 값 표시
  if(digitalRead(5)==LOW) {
    lcd.setCursor(0,0);
    lcd.print(      MAX      );
  }

  // 2번 버튼 누르면 초음파센서 거리 표시
  if(digitalRead(6)==LOW) {
    lcd.setCursor(0,0);
    lcd.print(    distance    );
  }

  // 3번 버튼 누르면 불균형도 표시
  if(digitalRead(7)==LOW) {
    lcd.setCursor(0,0);
    lcd.print(      RAN      );
  }
  
}
