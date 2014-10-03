/**
 * stripctrl - Simple Arduino sketch to accept commands to control a LPD8806 LED strip via Serial port
 * Author: Craig Calef <craig@dod.net>
 * This code is covered under the MIT License
 */
 
int LED = 13;

void setup() {
  Serial.begin(9600);     // opens serial port, sets data rate to 9600 bps
  
  // initialize digital pin 13 as an output.
  pinMode(LED, OUTPUT);
  for (int i = 0; i < 3; i++) {
    blinkLed();
  }
}

void blinkLed() {
  digitalWrite(LED, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(500);                // wait for a second
  digitalWrite(LED, LOW);    // turn the LED off by making the voltage LOW
  delay(500);                // wait for a second
}

void loop() {
  char incomingByte;
  int number = 0;
  int i;  
  if (Serial.available() > 0) { 
    incomingByte = (char) Serial.read();
    number = hexchartoi(incomingByte);
    for (i = 0; i < number; i++) {
      blinkLed();
    }
    Serial.print("I blinked ");
    Serial.print(number, DEC);
    Serial.println(" times");
  }
}

int hexchartoi(char a) {
  switch (a) {
    case '0': return 0;
    case '1': return 1;
    case '2': return 2;
    case '3': return 3;
    case '4': return 4;
    case '5': return 5;
    case '6': return 6;
    case '7': return 7;
    case '8': return 8;
    case '9': return 9;
    case 'A':
    case 'a': 
      return 10;
    case 'B': 
    case 'b':
      return 11;
    case 'C':
    case 'c': 
      return 12;
    case 'D':
    case 'd':
      return 13;    
    case 'E':
    case 'e':
      return 14;
    case 'F':
    case 'f':
      return 15;
    default:
      return 0;
  }
}
