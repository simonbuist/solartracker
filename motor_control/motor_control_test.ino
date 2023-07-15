#include <BluetoothSerial.h>
#include <Stepper.h>
#include <Wire.h>
#include <Adafruit_INA219.h>
// *** Bluetooth + Motor Setup. *** //
BluetoothSerial ESPbt;
const int in1 = 14;
const int in2 = 26; 
const int in3 = 27;
const int in4 = 25;
Stepper stepper(2038, in1, in2, in3, in4);


// *** Panel Reading + INA219 Setup. *** //
Adafruit_INA219 ina219;
// Define output pin 
int base = 4;
// Reporting frequency
float freq = 2; // Hz
// Delay after changing state of transistor
int del = 2; 
// Sensor variables 
float current_mA = 0;
float voltage = 0;
// Tracking time
unsigned long last = 0;
float t = 0;


void setup()
{
  // *** Read Bluetooth Data *** //
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
  Serial.print(intervalMinutes);
  intervalMillis = intervalMinutes * 60000;
  // intervalMillis = intervalMinutes * 100; // test code to go shorten the interval

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

  // *** Initialize INA219 for Power Reading *** //
  pinMode(base, OUTPUT);
  // pinMode(2, OUTPUT);
  Serial.begin(115200);
  while (!Serial) {
      // will pause Zero, Leonardo, etc until serial console opens
      delay(1);
  }
  if (! ina219.begin()) {
    Serial.println("Failed to find INA219 chip");
    while (1) { delay(10); }
  }
  ina219.setCalibration_16V_400mA();
  Serial.println("INA219 Ready!");
  last = millis();

  // Set up sampling intervals and arrays to collect readings.
  int numOfReadings = 10;
  int sample_interval = intervalMillis / numOfReadings; // 3 minutes
  int timestamps[numPositions*10];
  int voltage_readings[numPositions*10];
  int current_readings[numPositions*10];
  int idx = 0;
  int process_time;
  // *** Move motor and extract Power readings *** //
  // speed is in RPM
  stepper.setSpeed(3);
  int currPos = -283;
  process_time = millis();
  for (int i = 0; i < numPositions; i++) {
    stepper.step(positions[i] - currPos); // relative movement
    currPos = positions[i];
    Serial.println("Current Position: "); Serial.print(currPos);
    Serial.println();
    digitalWrite(in1, LOW); // set motor pins to low while not in use to save battery
    digitalWrite(in2, LOW);
    digitalWrite(in3, LOW);
    digitalWrite(in4, LOW);
    for (int i = 0; i < 10; i++) {
      // Get Voltage and Current readings.
      last = millis() - process_time;
      t = last/1000.0;
      digitalWrite(base, LOW);
      delay(del);
      // measure voltage
      voltage = ina219.getBusVoltage_V();

      delay(del);
      digitalWrite(base, HIGH); //and/or 
      delay(del);
      // measure current
      current_mA = ina219.getCurrent_mA();

      delay(del);

      // Store Voltage and Current readings.
      timestamps[idx] = t;
      Serial.print("{ ");
      Serial.print("Time: "); Serial.print(t); Serial.print(", ");
      voltage_readings[idx] = voltage;
      Serial.print("Voltage: "); Serial.print(voltage); Serial.print("V, ");
      current_readings[idx] = current_mA;
      Serial.print("Current: "); Serial.print(current_mA); Serial.print("mA }");
      Serial.println();
      delay(sample_interval);
    }
  }
}
void loop() {
}
