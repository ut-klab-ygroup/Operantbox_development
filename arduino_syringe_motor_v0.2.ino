
// Syringe Pump motor control rev0.2 06/10/2021  Chon-wa Cheong

// Rev History 
// Rev0.1 6/1/2021 : Initial code
// Rev0.2 6/8/2021 : Correct Motor parameter setting 
// Rev0.3 6/10/2021 : Correct some syntax and make it simple with reducing condition branch. 

#include <AccelStepper.h> 

#define X_SPEED 200 // X steps per second for Pull 
#define X_DOUBLE 400 // X steps per second for Push  
#define X_ACCEL 200 // X steps per second per second

#define EN        8    

#define X_DIR     5    // direction pin definition 
#define X_STP     2  // step pin definition 

#define BAUD_RATE 9600 // define serial baud rate 

AccelStepper stepper(AccelStepper::DRIVER, X_STP, X_DIR); // define motor driver mode 

int i;
int j;
int l; 
int m;
char x;

void setup() {
  Serial.begin(BAUD_RATE);

  stepper.setMaxSpeed(X_SPEED);
  stepper.setAcceleration(X_ACCEL);
  stepper.setSpeed(X_SPEED);

  Serial.println("<Adruino is ready");
  Serial.println("<Nose Poke touch? Y/N>");
  }

void loop() {
  
  if (Serial.available()>0) {
     char x= Serial.read();
     
    if ( x == 'Y' ){

    i = stepper.currentPosition(); 
      	stepper.moveTo(X_DOUBLE + i );  // set target position + current position
        while (stepper.currentPosition() != (i + X_DOUBLE )) // Full speed up to 400 + current position
        {
      	  stepper.run();
      	  stepper.stop();
          delay (500); 
        }
      
    j = stepper.currentPosition();
      	stepper.moveTo( j - X_SPEED ); // set new target position
        while (stepper.currentPosition() != j - X_SPEED ) // Full speed back  
        {
          stepper.run();
      	  stepper.stop();
        }
          Serial.println("water provided. Nose Poke touch again? Y/N? \n");
        

      else if ( x == 'N' ) {
        Serial.println("system stops and move back to initial position \n"); 
    l = stepper.currentPosition();
        stepper.moveTo ( 0 - l ); // move back to the origitnal position
        while (stepper.currentPosition() != 0 - l) 
        {
          stepper.run();
          stepper.stop();
        }
        Serial.println ("back to original position \n");
      }
     }
    }
  
  
