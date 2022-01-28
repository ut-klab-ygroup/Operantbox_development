#include <AccelStepper.h>
#include <MultiStepper.h>


// Syringe Pump motor control rev0.5 12/21/2021  Chon-wa Cheong

// Rev History
// Rev0.1 6/1/2021 : Initial code
// Rev0.2 6/8/2021 : Correct Motor parameter setting
// Rev0.3 6/16/2021 : Add external pin D0 as detection for water
// Rev0.4 7/26/2021 : change push parameter from 158 to 400 and pull 100
// Rev0.5 12/21/2021 : change external trigger with High for enable and Low for disable, add more comments and definition description.


#define PULL_POSITION_DELTA 50      // X steps pull position 
#define PUSH_POSITION_DELTA 100    // X steps push position 

#define X_DIR     5    // direction pin definition 
#define X_STP     2  // step pin definition 

#define BAUD_RATE 9600 // define serial baud rate 

AccelStepper stepper(AccelStepper::DRIVER, X_STP, X_DIR); // define motor driver mode

int k;      // Define the max number of times Motor can run until it gets stop
int i;      // Define Initial Motor Current position
int j;      // Define Motor current position after push (in order to define pull action)
int l;      // Not used
int m;      // Not used
int val;    // GPIO Trigger signal read from GPIO#3
char x;     // Not used


void setup() {
  pinMode (3, INPUT); // Input triggering for water, 5V water out, 0V stop
  pinMode (8, OUTPUT);  // used for test purpose only
  Serial.begin(BAUD_RATE);
  stepper.setMaxSpeed(500);   //max speed steps per second settiing
  stepper.setAcceleration(3000); // acceleration steps per second
  stepper.setSpeed(500);  // speed setting steps per second

  // stepper.setEnablePin(8);

  Serial.println("<Adruino is ready");
  Serial.println("<Nose Poke touch? Y/N>");
  k = 0 ;
  val = 0;
}

void loop() {

  // if (Serial.available()>0) {
  // char x= Serial.read();

  // stepper.enableOutputs();
  // stepper.disableOutputs();

  val = digitalRead(3);
  Serial.println(val);
  if (val == HIGH && k < 100000 ) {

    // if (x == 'Y' && k == 0) {
    // i = stepper.currentPosition();
    // stepper.moveTo(PULL_DELTA + i );  // set target position + current position
    // while (stepper.currentPosition() != (i + PULL_DELTA)) // Full speed up to 200 + current position
    // stepper.run();
    // stepper.stop();
    // delay(1000);

    //j = stepper.currentPosition();
    // stepper.moveTo(j - PULL_DELTA ); // set new target position as current position - 200
    // while (stepper.currentPosition() != j - PULL_DELTA) // Full speed back
    // stepper.run();
    // stepper.stop();
    // Serial.println("water provided, Nose Poke touch again? Y/N? \n");
    // k++ ;
    // }

    digitalWrite(8, LOW);
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
    delay(500);
    k++;
  }

  // Serial.println("water provided 2nd time, Nose Poke touch again? Y/N? \n");

  else {
    digitalWrite(8, HIGH);  // Used for testing purupose only
    //     Serial.println (val);

  }

}

//else if ( x == 'N' ) {
//  Serial.println("system stops and move back to initial position \n");
//  k = 0;
// l = stepper.currentPosition();
//  stepper.moveTo ( 0 - l ); // move back to the origitnal position
//  while (stepper.currentPosition() != 0 - l)
//  stepper.run();
//  stepper.stop();
// Serial.println ("back to original position \n");
//  }
