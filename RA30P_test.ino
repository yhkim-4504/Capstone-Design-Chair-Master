int LED = 13;

void setup() {
  // 센서값 측정위해 시리얼통신 준비
  Serial.begin(9600);
  pinMode(A0, INPUT);
  pinMode(13, OUTPUT);
}

void loop() {
  //아날로그 0번 핀에 압력센서를 연결
  int sensorval = analogRead(A0);
  
  // 입력을 통해 LED를 밝기를 조절
  if(analogRead(A0)==0) digitalWrite(LED, LOW);
  else digitalWrite(LED, HIGH);
  
  //시리얼 모니터를 통해 센서값 표기 
  Serial.print(sensorval);
  Serial.print(";");
  Serial.print(sensorval);
  Serial.print(";");
  Serial.println(sensorval);
  
  //100ms동안 대기
  delay(100);
}
