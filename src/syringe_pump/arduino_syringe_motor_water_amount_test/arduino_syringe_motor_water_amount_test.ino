#include <AccelStepper.h>
#include <MultiStepper.h>



#define PUSH_POSITION_DELTA 192    // X steps push position 
#define PULL_POSITION_DELTA 80      // X steps pull position 
#define ACCEL 60000
#define SPEED 5000
#define PUSH_MAX 100    // X steps push position 
#define INTERVAL 1000
#define X_DIR     5    // direction pin definition 
#define X_STP     2  // step pin definition 

#define BAUD_RATE 9600 // define serial baud rate 
#define DEBUG true
AccelStepper stepper(AccelStepper::DRIVER, X_STP, X_DIR); // define motor driver mode

int k;      // Define the max number of times Motor can run until it gets stop
int i;      // Define Initial Motor Current position
int j;      // Define Motor current position after push (in order to define pull action)
int val;    // GPIO Trigger signal read from GPIO#3



void setup() {
  pinMode (3, INPUT); // Input triggering for water, 5V water out, 0V stop

  Serial.begin(BAUD_RATE);


  k = 0 ;
  val = 0;
}

void loop() {


  while (digitalRead(3) == LOW) {
    delay(500);
  }
  // setting pinmode triggers electrical outputs, thereby heating up the motor.
  pinMode (8, OUTPUT);  // used for test purpose only
  stepper.setMaxSpeed(SPEED);   //max speed steps per second settiing
  stepper.setAcceleration(ACCEL); // acceleration steps per second
  stepper.setSpeed(SPEED);  // speed setting steps per second
  for (k = 0; k < PUSH_MAX; k++) {

    digitalWrite(8, LOW);  // Enable Motor
    if (DEBUG) {
      Serial.println("current");
      Serial.println(k);
      Serial.println(stepper.currentPosition());
    }

    i = stepper.currentPosition() - PUSH_POSITION_DELTA;
    if (DEBUG) {
      Serial.println("push");
      Serial.println(i);
    }

    stepper.moveTo( i ); // set new target position
    while (stepper.currentPosition() != i   ) // Full speed back
      stepper.run();

    delay(500);
    j = stepper.currentPosition() + PULL_POSITION_DELTA;
    if (DEBUG) {
      Serial.println("pull");
      Serial.println(j);
    }

    stepper.moveTo( j ); // set new target position
    while (stepper.currentPosition() != j   ) // Full speed back
      stepper.run();
    digitalWrite(8, HIGH);  // Disable Motor
    delay(INTERVAL);

  }
  stepper.setCurrentPosition(0);
  digitalWrite(8, HIGH);  // Disable Motor
}
