#include <AccelStepper.h>
#include <MultiStepper.h>


// Syringe Pump motor control rev0.5 12/21/2021  Chon-wa Cheong

// Rev History
// Rev0.1 6/1/2021 : Initial code
// Rev0.2 6/8/2021 : Correct Motor parameter setting
// Rev0.3 6/16/2021 : Add external pin D0 as detection for water
// Rev0.4 7/26/2021 : change push parameter from 158 to 400 and pull 100
// Rev0.5 12/21/2021 : change external trigger with High for enable and Low for disable, add more comments and definition description.



#define PUSH_POSITION_DELTA 192    // X steps push position 
#define PULL_POSITION_DELTA 70      // X steps pull position 
#define ACCEL 60000
#define SPEED 5000
#define PUSH_MAX 100    // X steps push position 

#define X_DIR     5    // direction pin definition 
#define X_STP     2  // step pin definition 

#define BAUD_RATE 9600 // define serial baud rate 

AccelStepper stepper(AccelStepper::DRIVER, X_STP, X_DIR); // define motor driver mode

int k;      // Define the max number of times Motor can run until it gets stop
int i;      // Define Initial Motor Current position
int j;      // Define Motor current position after push (in order to define pull action)
int val;    // GPIO Trigger signal read from GPIO#3



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

  k = 0 ;
  val = 0;
}

void loop() {

  // if (Serial.available()>0) {
  // char x= Serial.read();

  val = digitalRead(3);   
  Serial.println(val);
  if (val == HIGH && k < PUSH_MAX ) {

    digitalWrite(8, LOW);  // Enable Motor 
    i = stepper.currentPosition()-PUSH_POSITION_DELTA;
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
    while(digitalRead(3)==HIGH)
       delay(100);
       
    k++;
    
  }

    
    

}
