#include "cvzone.h"
#include "Servo.h"

Servo servo[5];
SerialData data(1, 5);
int value[5];

void setup() {
  data.begin(9600);
  servo[0].attach(3);
  servo[1].attach(5);
  servo[2].attach(6);
  servo[3].attach(9);
  servo[4].attach(10);
}

void loop() {
  data.Get(value);
  for (int i = 0; i < 5; i++) {
    servo[i].write(value[i]);
  }
  delay(30);
}
