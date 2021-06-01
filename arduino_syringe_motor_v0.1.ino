
// Syringe Pump motor control rev0.1 06/01/2021  Chon-wa Cheong

#include <AccelStepper.h> 

#define SPEED 1000 // steps per second
#define ACCEL 5000 // steps per second per second

#define DIR 5 // direction pin definition 
#define STP 2 // step pin definition 

#define BAUD_RATE 230400 // define serial baud rate 

AccelStepper Stepper(AccelStepper:: DRIVER, STP, DIR)  // define motor driver mode 

const int ledPin = 13; // define LED Pin


void setup() {
  Serial.begin(BAUD_RATE);

  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, HIGH):
  delay(500);
  digitalWrite(ledPin, LOW);
  delay(500);

  Stepper.setSpeed(SPEED);
  Stepper.setAcceleration(ACCEL);

  Serial.println("<Adruino is ready> \n");

void loop() {
  int i=0
  Serial.println("<Nose Poke touch? Y/N> \n");
  if (Serial.available()>0) {
     char x= Serial.Read();
     if (x == "Y" && i= 0 ) {
      Stepper.move(4000);  // about 1mm, to be verified 
      Stepper.run();
      Stepper.stop();
      delay(500);
      Stepper.move(-8000); // about 2mm, to be verified 
      Stepper.run();
      Stepper.stop();     
      Serial.println("water provided \n");
      i++ 
     }
      else if ( x == "Y" && i>0 ){
      	Stepper.move(8000);  // about 2mm, to be verified 
      	Stepper.run();
      	Stepper.stop();
      	delay(500);
      	Stepper.move(-8000); // about 2mm, to be verified
      	Stepper.run();
      	Stepper.stop();
        Serial.println("water provided \n");
      }
      else if ( x == "N" ) {
        Serial.println("system stops \n")
      }
   }
        
      
         
  

  

  
  