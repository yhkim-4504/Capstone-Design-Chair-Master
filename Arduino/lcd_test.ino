#include <Wire.h>
// 0x27

#include <LiquidCrystal_I2C.h>
#include <Wire.h>

// 0x3F I2C 주소를 가지고 있는 16x2 LCD객체를 생성합니다.(I2C 주소는 LCD에 맞게 수정해야 합니다.)
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  lcd.init();
  lcd.backlight();
  pinMode(2, INPUT_PULLUP);
  pinMode(3, INPUT_PULLUP);
  pinMode(4, INPUT_PULLUP);
}

void loop() { 
  lcd.setCursor(0,0);           // 0번째 줄 0번째 셀부터 입력하게 합니다.
  lcd.print("    CAPSTONE    ");  // 문구를 출력합니다.
  lcd.setCursor(0,1);           // 1번째 줄 0번째 셀부터 입력하게 합니다.
  lcd.print("     MUYAHO     ");
  if(digitalRead(2)==LOW) {
    lcd.setCursor(0,1);
    lcd.print("1");
  }
  if(digitalRead(3)==LOW) {
    lcd.setCursor(0,1);
    lcd.print("2");
  }
  if(digitalRead(4)==LOW) {
    lcd.setCursor(0,1);
    lcd.print("3");
  }
  /*
  delay(500);
  lcd.clear();
  delay(500);
  */
}
