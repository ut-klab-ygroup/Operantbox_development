
Arduino Operant Motor Control Design v0.1 (05/31/2021)

High Level Architecture design (1st phase, current code design) : 

1. Initial parameters setup
2. Initial system setup 
3. Loop creation
    (add parameter for counting)  
    3-1 Send message asking for nose poke touch? 
    3-2 If receive "yes", check initial parameter, if it is first time, 
        Do One push action 
        Do One pull action
        Counter increment  
    3-3 go back to 3-1, look for another nose poke touch? 
    3-4 If receive "yes", check parameter, if it is second time, 
        Do One New push action 
        Do One pull action
        Counter increment 
        go back to 3-1, and repeat 
    3-5 If counter reaches "one defined number" 
    3-6 Return 0 (finish the program, no water) 

Software allows parameter changes for 1) Number of evolution 
                                      2) Number of steps per second (RPM) (Revolution per minute)


High Level Architecture design (2nd phase) : 

"Send message" portion can be changed to "nose poke" detection for automotic nose poke detection 
"Noke poke sensor can be connected to Arduino digital input to verify this detection and water supply


High Level Architecture design (3rd phase) : 

Integrate control from Python/Pycharm (PC or Raspberry Pi) 

One motor version : 

1. Bring up serial (USB) 
2. Send "Ready" to Host
3. Ask to start the work to Host? 
4. If Y, then start
5. continue polling, if N, then stop 
6. Once nose poke detects and water is supplied, send notification message to Host (no ack is needed)
7. Python continues to collect notification message for log collection (Python can measure time when it receive the notification)



















