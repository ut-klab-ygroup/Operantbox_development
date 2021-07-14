
// Syringe Pump motor control rev0.2 06/08/2021  Chon-wa Cheong

// Rev History 
// Rev0.1 6/1/2021 : Initial code
// Rev0.2 6/8/2021 : Correct Motor parameter setting 
// Rev0.3 6/16/2021 : Add external pin D0 as detection for water

#include <AccelStepper.h> 

#define X_SPEED 64      // X steps pull position 
#define X_DOUBLE 158    // X steps push position 
#define X_ACCEL 8       // no meaning 

#define EN        8    

#define X_DIR     5    // direction pin definition 
#define X_STP     2  // step pin definition 

#define BAUD_RATE 9600 // define serial baud rate 

AccelStepper stepper(AccelStepper::DRIVER, X_STP, X_DIR); // define motor driver mode 

int k; 
int i;
int j;
int l; 
int m;
int val;
char x;


void setup() {
  pinMode (3, INPUT); 
  pinMode (8, OUTPUT); 
  Serial.begin(BAUD_RATE);
  stepper.setMaxSpeed(500);   //max speed steps per second settiing 
  stepper.setAcceleration(6000); // acceleration steps per second per second 
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
   
    if (val == HIGH && k < 100 ) {

     // if (x == 'Y' && k == 0) {
     // i = stepper.currentPosition(); 
     // stepper.moveTo(X_SPEED + i );  // set target position + current position
     // while (stepper.currentPosition() != (i + X_SPEED)) // Full speed up to 200 + current position 
     // stepper.run();
     // stepper.stop();
     // delay(1000);

     //j = stepper.currentPosition();    
     // stepper.moveTo(j - X_SPEED ); // set new target position as current position - 200 
     // while (stepper.currentPosition() != j - X_SPEED) // Full speed back
     // stepper.run();
     // stepper.stop();     
     // Serial.println("water provided, Nose Poke touch again? Y/N? \n");
     // k++ ; 
     // }
     
        digitalWrite(8, LOW); 
    i = stepper.currentPosition(); 
      	stepper.moveTo(X_DOUBLE + i );  // set target position + current position
        while (stepper.currentPosition() != (i + X_DOUBLE )) // Full speed up to 400 + current position
      	stepper.run();
        stepper.stop();
      	delay(500);
        
    j = stepper.currentPosition();
        stepper.moveTo( j - X_SPEED ); // set new target position
        while (stepper.currentPosition() != j - X_SPEED ) // Full speed back  
   	    stepper.run();
        stepper.stop();
        delay(500);
        k++;
     }
     
     // Serial.println("water provided 2nd time, Nose Poke touch again? Y/N? \n");
       
      else {
        digitalWrite(8, HIGH);
     // Serial.println (val);
        
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
    

  
  
