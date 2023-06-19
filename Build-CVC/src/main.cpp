#include <Arduino.h>


float R_2 = 10000;
int pwm = 0;


void setup(){

  analogReference(EXTERNAL);

  pinMode(3, OUTPUT);
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);

  Serial.begin(9600);

  map(pwm, 0, 1023, 0, 255);
  pwm = constrain(pwm, 0, 255);

}


void loop(){

  pwm++;
  
  if(pwm == 255)
    Serial.end();
  
  analogWrite(3, pwm);

  Serial.print(analogRead(A1));
  Serial.print(";");
  Serial.print((analogRead(A0) - analogRead(A1)) / R_2);

}