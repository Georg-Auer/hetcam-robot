#include <AccelStepper.h>
// https://www.pjrc.com/teensy/td_libs_AccelStepper.html
//configure AccelStepper to mode 1 (Step/Dir)
int board1 = 1;
//define Pins
int motor0_en = 1;
int motor0_dir = 2;
int motor0_step = 3;

int motor1_en = 4;
int motor1_dir = 5;
int motor1_step = 6;

int motor2_en = 7;
int motor2_dir = 8;
int motor2_step = 9;

int motor3_en = 10;
int motor3_dir = 11;
int motor3_step = 12;

//define Pins on AccelStepper library
AccelStepper motor0(board1, motor0_step, motor0_dir);
AccelStepper motor1(board1, motor1_step, motor1_dir);
AccelStepper motor2(board1, motor2_step, motor2_dir);
AccelStepper motor3(board1, motor3_step, motor3_dir);//...(1[means driver board], step, dir)

struct STRUCT {
  int motor0_enable = 1;
  int motor0_direction;
  int motor0_position;
  int motor1_enable = 1;
  int motor1_direction;
  int motor1_position;
  int motor2_enable = 1;
  int motor2_direction;
  int motor2_position;
  int motor3_enable = 1;
  int motor3_direction;
  int motor3_position;
} testStruct;

#include "SerialTransfer.h"

int ledPin = 13;     // pin that the led is attached to
//int analogvalue = 0;

SerialTransfer myTransfer;

void setup()  
  {       
  
  //TODO: enable/disable motors from python
  
  //enable motors
  pinMode (motor0_en, OUTPUT); //motor0_EN
  pinMode (motor1_en, OUTPUT); //motor1_EN
  pinMode (motor2_en, OUTPUT); //motor2_EN
  pinMode (motor3_en, OUTPUT); //motor3_EN
  //motors on/off
  digitalWrite (motor0_en, HIGH); //motor0 HIGH:off, LOW:on
  digitalWrite (motor1_en, HIGH); //motor1
  digitalWrite (motor2_en, HIGH); //motor2
  digitalWrite (motor3_en, HIGH); //motor3
  
  motor0.setMaxSpeed(20000);  //always necessary, default very slow
  motor1.setMaxSpeed(20000); 
  motor2.setMaxSpeed(20000);
  motor3.setMaxSpeed(20000); 
  
  Serial.begin(115200);
  myTransfer.begin(Serial);

  //for testing purposes
  pinMode(ledPin, OUTPUT);  //set switch as input pin for rawdata-mode
  digitalWrite (ledPin, LOW);
}

void loop()  
{

  if(myTransfer.available())
  {
    // find size of transferred message
    uint16_t recSize = 0;
    recSize = myTransfer.rxObj(testStruct, recSize);
    
    // do the enable here, otherwise the stop condition and the motorX_en interfere
    digitalWrite (motor0_en, testStruct.motor0_enable); //motor0
    digitalWrite (motor1_en, testStruct.motor1_enable); //motor1
    digitalWrite (motor2_en, testStruct.motor2_enable); //motor2
    digitalWrite (motor3_en, testStruct.motor3_enable); //motor3

    
    // send all received data back to Python
    for(uint16_t i=0; i < myTransfer.bytesRead; i++)
      myTransfer.packet.txBuff[i] = myTransfer.packet.rxBuff[i];
    
    myTransfer.sendData(myTransfer.bytesRead);
  }

  motor0.moveTo(testStruct.motor0_position);
  motor1.moveTo(testStruct.motor1_position);
  motor2.moveTo(testStruct.motor2_position);
  motor3.moveTo(testStruct.motor3_position);

  motor0.setSpeed(700);
  motor1.setSpeed(700);
  motor2.setSpeed(700);
  motor3.setSpeed(700);

  motor0.runSpeedToPosition();  
  motor1.runSpeedToPosition();
  motor2.runSpeedToPosition();
  motor3.runSpeedToPosition();

  if (motor0.distanceToGo()== 0){
    delay(500);
    digitalWrite (motor0_en, HIGH); //motor0
    //delay(500);
    testStruct.motor0_enable = 1; // turn motor off after distanceToGo is 0
  }
  if (motor1.distanceToGo()== 0){
    digitalWrite (motor1_en, HIGH); //motor1
    testStruct.motor1_enable = 1;
  }
  if (motor2.distanceToGo()== 0){
    digitalWrite (motor2_en, HIGH); //motor2
    testStruct.motor2_enable = 1;
  }
  if (motor3.distanceToGo()== 0){
    digitalWrite (motor3_en, HIGH); //motor3
    testStruct.motor3_enable = 1;
  } 
}  
