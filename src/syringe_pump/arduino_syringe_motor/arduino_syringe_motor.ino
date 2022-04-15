#include <AccelStepper.h>
#include <MultiStepper.h>

#define PUSH_POSITION_DELTA 192    // X steps push position 
#define PULL_POSITION_DELTA 80      // X steps pull position 
#define RESET_POSITION_DELTA 1000000    // X steps pull position 
#define ACCEL 60000
#define SPEED 5000
#define PUSH_MAX 8000    // X steps push position 5ml syringe, 0.5ul for each

#define X_DIR     5    // direction pin definition 
#define X_STP     2  // step pin definition 

#define BAUD_RATE 9600 // define serial baud rate 

#define DEBUG false

AccelStepper stepper(AccelStepper::DRIVER, X_STP, X_DIR); // define motor driver mode

int k;      // Define the max number of times Motor can run until it gets stop
int i;      // Define Initial Motor Current position
int j;      // Define Motor current position after push (in order to define pull action)
int val;    // GPIO Trigger signal read from GPIO#3
char incomingByte = 0; // for incoming serial data

void setup() {
  pinMode (3, INPUT); // Input triggering for water, 5V water out, 0V stop
  pinMode (8, OUTPUT);  // used to control motor enable/disable
  Serial.begin(BAUD_RATE);
  stepper.setMaxSpeed(SPEED);   //max speed steps per second settiing
  stepper.setAcceleration(ACCEL); // acceleration steps per second
  stepper.setSpeed(SPEED);  // speed setting steps per second

  // stepper.setEnablePin(8);
  digitalWrite(8, HIGH);  // disable motor
  Serial.println("<Adruino is ready");
  Serial.print ("Enter p to pullback, s to stop, u to push");
  k = 0 ;
  val = 0;
}

void loop() {

  val = digitalRead(3);
  if(DEBUG){
    Serial.println(val);
  }

  // reset position to avoid saturatoin
  stepper.setCurrentPosition(0);

  
  if (val == HIGH && k < PUSH_MAX ) {
    Serial.println("Trigger detected");
    digitalWrite(8, LOW);  // Enable Motor
    i = stepper.currentPosition() - PUSH_POSITION_DELTA;
    stepper.moveTo(  i );  // set target position + current position
    while (stepper.currentPosition() != i) // Full speed up to 400 + current position
      stepper.run();

    stepper.stop();
    delay(500);

    j = stepper.currentPosition() + PULL_POSITION_DELTA;
    stepper.moveTo( j ); // set new target position
    while (stepper.currentPosition() != j  ) // Full speed back
      stepper.run();

    stepper.stop();
    digitalWrite(8, HIGH);  // disable motor
    // wait until pulse end. only 1 push for each high
    while (digitalRead(3) == HIGH)
      delay(100);

    k++;
  }

  if (Serial.available() > 0) {
    // read incoming bytes
    incomingByte = Serial.read();
    
    if (incomingByte == 'p') {
      Serial.print("Pull start");
      digitalWrite(8, LOW); // Enable motor
      j = stepper.currentPosition() + RESET_POSITION_DELTA;
      stepper.moveTo( j ); // set new target position
      while (stepper.currentPosition() != j||Serial.read()!='s' ){
        stepper.run();
        Serial.println(".");
      } 
      Serial.println("End");
      // stepper.stop();
      digitalWrite(8, HIGH); // disable motor
      k=0;
    }

    if (incomingByte == 'u') {
      Serial.print("Push");
      digitalWrite(8, LOW); // Enable motor
      j = stepper.currentPosition() - RESET_POSITION_DELTA;
      stepper.moveTo( j ); // set new target position
      while (stepper.currentPosition() != j||Serial.read()!='s' ){ // Full speed back
        stepper.run();
        Serial.println(".");
      }
      Serial.println("End");
      // stepper.stop();
      digitalWrite(8, HIGH); // disable motor
      k=0;
    }

  }

}
