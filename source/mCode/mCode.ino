/*
This is the first verion of code for the Arduino Mega 2560 for the pour machine
finished by Jun on Aug 8th 2013
Note: Code may not be very efficient but functional
Some variables maybe unused and several lines seem doing nothing. 
Will delete them when having a chance to test the machine. Just for not making mistakes
*/

//assign pins
//digital Pins
int verPul = 10; //vertial pulse 
int verDir = 11; //vertial direction
int cruPul = 26; //crucible pulse 
int cruDir = 27; //crucible direction
int basPul = 22; //base pulse
int basDir = 23; //base direction
int indicator = 13; //just a indicator, not currently used.

int verTog = 50; //toggle switch for vertical motor
int cruTog = 51; //toggle switch for crucible motor
int basTog = 52; //toggle switch for base motor

//analog Pins for input
int verPot = 0; //pot for vertial
int cruPot = 1; //pot for crucible
int basPot = 2; //pot for base

int verSwTop = 8; //limit switch for vertical top
int verSwBtm = 7; //limit switch for vertical bottom
int cruSwBck = 3; //limit switch for crucible back
int basSwCW = 6; //limit switch for base clockwise
int basSwCCW = 5; //limit switch for base counter clockwise

//set all motors' hold time (determine motors' speed)
int intTime = 1;

//variables used in this program (some of them maybe unused) 
int verDirect = LOW; //pin output -- vertical direction
int verDirectMark = 0;//
int cruDirect = LOW; //pin output -- crucible direction
int cruDirectMark = 0;//
int basDirect = LOW; //pin output -- vertical direction
int basDirectMark = 0;//

int verDirectPre = LOW; //pin output of previous loop -- vertical direction
int cruDirectPre = LOW;//pin output of previous loop -- crucible direction
int basDirectPre = LOW;//pin output of previous loop -- base direction

//variables determine the motors' status
int verDig = LOW; //pin output -- vertical pulse (digitial output)
int cruDig = LOW; //pin output -- crucible pulse (digitial output)
int basDig = LOW; //pin output -- base pulse (digitial output)

int verDigPre = LOW; //pin output of previous loop -- vertical pulse (digitial output)
int cruDigPre = LOW; //pin output of previous loop -- crucible pulse (digitial output)
int basDigPre = LOW; //pin output of previous loop -- base pulse (digitial output)

//clutch for the crucible
int cruCluI = 0; //clutch counter
int cruClutch = 0; // crucible clutch marker
int cruClutchPre = -1; // crucible clutch marker of previous loop

//variables for replay
String strInput, strcmdLoop, st; //command input
int cmdLoop; //amount of loops should run at the current status
const int arraySize = 20; // array size
String stArray[arraySize]; // array for storing command 

int ist = 0; 
int i = 0;
long iloop = 0; 
long iloopPre = 0;
long cloop = 0;

void setup()
{ // initialize
  pinMode(verPul,OUTPUT);
  pinMode(verDir,OUTPUT);
  pinMode(verPot,INPUT);
  pinMode(cruPul,OUTPUT);
  pinMode(cruDir,OUTPUT);
  pinMode(cruPot,INPUT);
  pinMode(basPul,OUTPUT);
  pinMode(basDir,OUTPUT);
  pinMode(basPot,INPUT);
  pinMode(indicator,OUTPUT);
  pinMode(verTog,INPUT);
  pinMode(cruTog,INPUT);
  pinMode(basTog,INPUT);
  pinMode(verSwTop,INPUT);
  pinMode(verSwBtm,INPUT);
  pinMode(cruSwBck,INPUT);
  pinMode(basSwCW,INPUT);
  pinMode(basSwCCW,INPUT);
  digitalWrite(indicator,LOW);
  Serial.begin(9600);
}

void loop()
{ 
  // read a serial input
  if(Serial.available()){
    int Mark = Serial.read(); // save the input     
    //'g' for dial mode
    iloop = 0; // start to count loop in dial mode
    while(Mark=='g' && !Serial.available()) { 
      //Serial.println('g');
      //read input from dials, limit switches and toggle switches 
      int A0verPot = analogRead(verPot);
      int A1cruPot = analogRead(cruPot);
      int A2basPot = analogRead(basPot);
      int AIverSwTop = analogRead(verSwTop);
      int AIverSwBtm = analogRead(verSwBtm);
      int AIcruSwBck = analogRead(cruSwBck);
      int AIbasSwCW = analogRead(basSwCW);
      int AIbasSwCCW = analogRead(basSwCCW);
      int DIverTog = digitalRead(verTog);
      int DIcruTog = digitalRead(cruTog);
      int DIbasTog = digitalRead(basTog); 
    
      //determine the vertical motor's pulse according to readings
      if(DIverTog == HIGH){ //toggle switch
        if(A0verPot>=312 && A0verPot<=712){ //dial
          verDig = LOW;
        } 
        else {
          //
          if(AIverSwTop<512 && A0verPot>=512){
            verDig = LOW;
          }
          else if(AIverSwBtm<512 && A0verPot<512){
            verDig = LOW;
          }
          else{
            verDig = HIGH;
          }
        }
       }
       else{
         verDig = LOW;
       }
      
      //similar to vertical motion
      if(DIcruTog == HIGH){
        if(A1cruPot>=312 && A1cruPot<=712){
          cruDig = LOW;
          cruClutch=-1;
        } 
        
        else if(A1cruPot<=150 || A1cruPot>=912){
           cruClutch = 0; //crucible clutch marker, 0 mean no loop is ignored for the crucible motor (fastest mode)
           cruClutchSub(); // count cruCluI for the crucible motor
           if (cruCluI==0) {           
             if (AIcruSwBck<512 and A1cruPot<512){ //determine the crucible motor's status (pulse/direction)
               cruDig = LOW;
             }
             else{
               cruDig = HIGH; 
             }            
           }
           else {cruDig = LOW;} 
        }
        else {
           cruClutch = 3; //crucible clutch marker, 3 means 3 loops are ignored for the crucible motor
           cruClutchSub();
           if (cruCluI==0) {
             if (AIcruSwBck<512 and A1cruPot<512){
               cruDig = LOW;
             }
             else{
               cruDig = HIGH; 
             }     
         }
           else {cruDig = LOW; } 
        }
      }
      else{
          cruDig = LOW;
          cruClutch=-1; //crucible cluth marker, -1 means crucible motor is off
      }
      
      // same as the vertical motor
      if (DIbasTog == HIGH){
        if(A2basPot>=312 && A2basPot<=712){
          basDig = LOW;
        } 
        else {
          //switch function
          if(AIbasSwCW<512 && A2basPot>=512){
            basDig = LOW;
          }
          else if(AIbasSwCCW<512 && A2basPot<512){
            basDig = LOW;
          }
          else{
            basDig = HIGH;
           // Serial.println("High");
          }
        }
      }
      else{
        basDig = LOW;
      }      
      
      //determine the vertical motor's direction according to readings
      if(A0verPot>=512){
        verDirect = LOW;
      } 
      else {
        verDirect = HIGH;
      }
      if(A1cruPot>=512){
        cruDirect = LOW;
      } 
      else {
        cruDirect = HIGH;
      }
      
      if(A2basPot>=512){
        basDirect = LOW;
      } 
      else {
        basDirect = HIGH;
      }
     
      runMotor(); // run motor subroutine, pulse/direction has been determined by 
      opLog(); // log data subroutine
      iloop = iloop+1; // count loops
      
      // remember information of the previous step
      verDigPre = verDig; 
      verDirectPre = verDirect;
      cruDigPre = cruDig;
      cruDirectPre = cruDirect;      
      basDigPre = basDig;
      basDirectPre = basDirect;     
      cruClutchPre = cruClutch;
//      Serial.print(iloop);      
//      Serial.print(',');
//      Serial.print(verDig);
//      Serial.print(',');
//      Serial.print(verDirect);      
//      Serial.print(',');
//      Serial.print(cruDig);     
//      Serial.print(',');
//      Serial.print(cruDirect);
//      Serial.print(',');
//      Serial.print(basDig);      
//      Serial.print(',');
//      Serial.println(basDirect);
    }
    
    //command mode
    int modeCheck = 'r'; // replay mode check. if it is 'q', then quit replay mode.
    if(Mark=='r') initializeData(); // initialize variables
    while(Mark=='r' && modeCheck!='q') // serial input 'r' for replay mode
    { 
      strInput = String(""); // initialize strInput
      while(Serial.available())
      {
        strInput = strInput+char(Serial.read());
        delay(1); //delay is necessary! give enough time to read a complete line
      }
      if(strInput.indexOf("|")>=0) // "|" is a must have symbol for a command, it's actually a seperator
      { // read multiple commands into the array stAarray
        stArray[ist]=String(strInput); 
//        Serial.println(stArray[ist]);
        ist=ist+1;
      }
      else if (strInput.indexOf("QUIT")>=0) //"QUIT" for completing input command and run those inputed commands
      {
        modeCheck='q';
//        for(i=0;i<=ist-1;i++)
//        {
//          Serial.println(stArray[i]);
//        }        
//        Serial.println("Quit Command Input.");
      }
     }
     
     //start run the commands stored in the array strArray
     if(Mark=='r')
     {
//        for(i=0;i<=ist-1;i++)
//        {
//          Serial.println(stArray[i]);
//        } 
       for(i=0;i<=(ist-1);i++)
       { 
         cloop = 1; // loop counter in replay mode. Start from 1 because in the following if statement, <= is used, not <
         st = String(stArray[i]); //read a command in the array to st
         parseData(); // parse the command to get cmdLoop -- the amount of loop run for the command line
//         Serial.println(i);
//         Serial.println(cloop);
//         Serial.println(cmdLoop);
        // run commands sequentially
         while(cloop<=cmdLoop)
         { 
           //translate command to the output for pins
           //vertial motor
           if(st.indexOf("VERPULON")>=0) verDig = HIGH;
           if(st.indexOf("VERDIRDOWN")>=0) {verDirect = HIGH;}
           else {verDirect = LOW;}
           
           //crucible motor. a little bit complicated. use cruClutchSub to adjust speed.
           if(st.indexOf("CRUPULONA")>=0){
             cruClutch = 0;
             cruClutchSub();
             if (cruCluI==0) {cruDig = HIGH;}
             else {cruDig = LOW;}
           }
           if(st.indexOf("CRUPULONB")>=0){
             cruClutch = 3;
             cruClutchSub();
             if (cruCluI==0) {cruDig = HIGH;}
             else {cruDig = LOW;}
           }
           if(st.indexOf("CRUPULONC")>=0){
             cruClutch = 6;
             cruClutchSub();
             if (cruCluI==0) {cruDig = HIGH;}
             else {cruDig = LOW;}
           }
           
           if(st.indexOf("CRUDIRBACK")>=0) {cruDirect = HIGH;}
           else {cruDirect = LOW;}
           
           if(st.indexOf("BASPULON")>=0) basDig = HIGH;
           if(st.indexOf("BASDIRCCW")>=0) {basDirect = HIGH;}
           else {basDirect = LOW;}
           runMotor();
           cloop = cloop+1;
         }
         
         //initialize? I don't think it's useful here.         
         verDig = LOW;
         verDirect = LOW;
         cruDig = LOW;
         cruDirect = LOW;
         basDig = LOW;
         basDirect= LOW;
       }
     }
  }
}

//subroutines
void parseData() // parse command line to get cmdLoop
{
   if(st.indexOf("|")>=0)
   {
     strcmdLoop = st.substring(st.indexOf("|")+1);
     cmdLoop = strcmdLoop.toInt();
   }
   else
   {
     cmdLoop = 0;
   }
   //Serial.println(cmdLoop);
}

//initialize stArray
void initializeData()
{
  ist = 0;
  for(i=0;i<arraySize;i++)
  {
    stArray[i] = String("NONE");
  }
}

//clutch for the crucible
void cruClutchSub()
{
  if (cruCluI<cruClutch) 
  {
    cruCluI = cruCluI+1;
  }
  else 
  {
    cruCluI = 0;
  }
}

//run motor
void runMotor()
{  
  //direction
  digitalWrite(verDir,verDirect);
  digitalWrite(cruDir,cruDirect);
  digitalWrite(basDir,basDirect);
  //pulse
  digitalWrite(verPul,verDig);
  digitalWrite(cruPul,cruDig);
  digitalWrite(basPul,basDig);
  digitalWrite(indicator,HIGH);
  delay(intTime);
  digitalWrite(verPul,LOW);
  digitalWrite(cruPul,LOW);
  digitalWrite(basPul,LOW);
  digitalWrite(indicator,LOW);
  delay(intTime);
}

void stopMotor()
{  
  //direction
  digitalWrite(verDir,verDirect);
  digitalWrite(cruDir,cruDirect);
  digitalWrite(basDir,basDirect);
  //pulse
  digitalWrite(verPul,LOW);
  digitalWrite(cruPul,LOW);
  digitalWrite(basPul,LOW);
  delay(intTime);
  digitalWrite(verPul,LOW);
  digitalWrite(cruPul,LOW);
  digitalWrite(basPul,LOW);
  delay(intTime);
}

//log data
void opLog()
{  // log data when status change, if statements is for determine whether status has changed or not.
  if(verDig!=verDigPre || (verDirectPre!=verDirect && ( verDig!=LOW && verDigPre!=LOW)) || cruClutch!=cruClutchPre || (cruDirectPre!=cruDirect && (cruClutch!=-1 && cruClutchPre!=-1)) || basDig!=basDigPre || (basDirectPre!=basDirect &&(basDig!=LOW && basDigPre!=LOW)))
  { 
    if (iloop!=0){// not to log at the first loop
    //vertical
      if (verDigPre==1){ //IMPORTANT, ...Pre (status at the previous loop) should be logged, not the current one. Current status has changed
        Serial.print("VERPULON");
      }
      else{
        Serial.print("VERPULOFF");
      }
      Serial.print(',');
      if(verDirectPre==0){
        Serial.print("VERDIRUP");
      }
      else{
        Serial.print("VERDIRDOWN");
      }
      //crucible
      Serial.print(',');
      if (cruClutchPre==0){
        Serial.print("CRUPULONA");
      }
      else if (cruClutchPre==3){
        Serial.print("CRUPULONB");
      }
      else if (cruClutchPre==6){
        Serial.print("CRUPULONC");
      }
      else{
        Serial.print("CRUPULOFF");
      }
      Serial.print(',');
      if(cruDirectPre==0){
        Serial.print("CRUDIRPOUR");
      }
      else{
        Serial.print("CRUDIRBACK");
      }
      Serial.print(',');
        
      //base
      if (basDigPre==1){
        Serial.print("BASPULON");
      }
      else{
        Serial.print("BASPULOFF");
      }
      Serial.print(',');
      if(basDirectPre==0){
        Serial.print("BASDIRCW");
      }
      else{
        Serial.print("BASDIRCCW");
      }     
      
      Serial.print("|");
      int hloop = iloop-iloopPre; // count the amount of loops run at the current status
      Serial.println(hloop); //save the amount of loops
      iloopPre = iloop;
    }
  }
}


