#include <AccelStepper.h>
#include <MultiStepper.h>



#define PUSH_POSITION_DELTA 200    // X steps push position 
#define PULL_POSITION_DELTA 150      // X steps pull position 
#define ACCEL 2000
#define SPEED 500
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
  pinMode (8, OUTPUT);  // used for test purpose only
  Serial.begin(BAUD_RATE);
  stepper.setMaxSpeed(SPEED);   //max speed steps per second settiing
  stepper.setAcceleration(ACCEL); // acceleration steps per second
  stepper.setSpeed(SPEED);  // speed setting steps per second

  k = 0 ;
  val = 0;
}

void loop() {


  while (digitalRead(3) == LOW) {
    delay(100);
  }

  for (k = 0; k < PUSH_MAX; k++) {

    digitalWrite(8, LOW);
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

    delay(500);
  }

}
