#include <BluetoothSerial.h>
#include <Stepper.h>

BluetoothSerial ESPbt;

const int in1 = 14;
const int in2 = 26; 
const int in3 = 27;
const int in4 = 25;

Stepper stepper(2038, in1, in2, in3, in4);

void setup()
{
  ESPbt.begin("ESP32_SYDE361");
  Serial.begin(115200);
  Serial.println("Waiting for Start Signal...");

  int intervalMinutes;
  int intervalMillis;
  int numPositions;

  // wait until input is sent for the interval
  while(!ESPbt.available()) 
    delay(10);
  // read the interval - each value is delimited by a .
  intervalMinutes = ESPbt.readStringUntil('.').toInt();
  // intervalMillis = intervalMinutes * 60000;
  intervalMillis = intervalMinutes * 100; // test code to go shorten the interval

  // similar to above for positions array
  while(!ESPbt.available()) 
    delay(10);
  numPositions = ESPbt.readStringUntil('.').toInt(); // need to find number of positions to create the array
  int positions[numPositions];
  for (int i = 0; i < numPositions; i++) {
    while(!ESPbt.available()) 
      delay(50);
    positions[i] = ESPbt.readStringUntil('.').toInt();
  }
  
  // speed is in RPM
  stepper.setSpeed(3);
  int currPos = -283;
  for (int i = 0; i < numPositions; i++) {
    stepper.step(positions[i] - currPos); // relative movement
    currPos = positions[i];
    Serial.println(currPos);
    digitalWrite(in1, LOW); // set motor pins to low while not in use to save battery
    digitalWrite(in2, LOW);
    digitalWrite(in3, LOW);
    digitalWrite(in4, LOW);
    delay(intervalMillis);

  }
}

void loop() {}
