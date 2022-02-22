#include <AccelStepper.h>
#include <MultiStepper.h>

#define PULL_POSITION_DELTA 1000    // X steps pull position 
#define ACCEL 60000
#define SPEED 5000

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
  pinMode (8, OUTPUT);  // Motor enable/disable control 
  Serial.begin(BAUD_RATE);
  stepper.setMaxSpeed(5000);   //max speed steps per second settiing
  stepper.setAcceleration(60000); // acceleration steps per second
  stepper.setSpeed(5000);  // speed setting steps per second

  // stepper.setEnablePin(8);
  digitalWrite(8, HIGH);  // disable motor
  Serial.println("<Adruino is ready");

}

void loop() {
  if (Serial.available() > 0) {
    // read incoming bytes
    incomingByte = Serial.read();
    Serial.print ("Please enter "p" to pullback");
    stepper.setCurrentPosition(0);
    if (incomingByte == 'p') {
      Serial.print ("Pull");
      digitalWrite(8, LOW); // Enable motor
      stepper.setCurrentPosition(0);
  j = stepper.currentPosition() + PULL_POSITION_DELTA;
  stepper.moveTo( j ); // set new target position
  while (stepper.currentPosition() != j ) // Full speed back
    stepper.run();

  stepper.stop();
  digitalWrite(8, HIGH); // disable motor
    }
    else {
      Serial.print ("wrong character, please enter again")
    }
  }
}
