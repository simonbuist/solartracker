#include <BluetoothSerial.h>
#include <Stepper.h>

BluetoothSerial ESPbt;

const int in1 = 14;
const int in2 = 27; 
const int in3 = 26;
const int in4 = 25;

long start = 0;

// Bluetooth Event Handler CallBack Function Definition
// If we don't pay attention to congestion (cong) 
// the buffer will fill and messages will stop being sent.
// The BluetoothSerial will also start blocking code execution 
// for a certain time interval when the buffer is full. 

bool cong = false; 

void BT_EventHandler(esp_spp_cb_event_t event, esp_spp_cb_param_t *param) {
  if (event == ESP_SPP_START_EVT) {
    Serial.println("Initialized SPP");
  }
  else if (event == ESP_SPP_SRV_OPEN_EVT ) {
    Serial.println("Client connected");
  }
  else if (event == ESP_SPP_CLOSE_EVT  ) {
    Serial.println("Client disconnected");
  }
  else if (event == ESP_SPP_CONG_EVT){
    cong = true;
    Serial.println("Client not listening");
  }
}

Stepper stepper(2038, in1, in2, in3, in4);
// AccelStepper stepper(AccelStepper::FULL4WIRE, in1, in3, in2, in4);

void setup()
{
  // stepper.setMaxSpeed(100);
  // stepper.setAcceleration(20);

  start = millis();

  ESPbt.begin("ESP32_SYDE361");
  Serial.begin(115200);

  Serial.println("Waiting for Start Signal...");

  while(!ESPbt.available()) 
    delay(500);
  // if (ESPbt.available()){  
  //   Serial.print(ESPbt.readString());  
  //   Serial.print('\n');
  // }

  // register the callbacks defined above (most important: congestion)
  ESPbt.register_callback(BT_EventHandler);

  ESPbt.print("ready");

  // stepper.disableOutputs();

  int intervalMinutes;
  int intervalMillis;
  int numPositions;
  Serial.println("waiting for input");

  while(!ESPbt.available()) 
    delay(10);
    
  intervalMinutes = ESPbt.readStringUntil('.').toInt();
  // intervalMillis = intervalMinutes * 60000;
  intervalMillis = intervalMinutes * 1000;

  while(!ESPbt.available()) 
    delay(10);
  numPositions = ESPbt.readStringUntil('.').toInt();

  int positions[numPositions];
  for (int i = 0; i < numPositions; i++) {
    while(!ESPbt.available()) 
      delay(50);
    positions[i] = ESPbt.readStringUntil('.').toInt();
  }
  
  stepper.setSpeed(3);
  int currPos = 0;
  for (int i = 0; i < numPositions; i++) {
    stepper.step(positions[i] - currPos);
    currPos = positions[i];
    Serial.println(currPos);
    delay(intervalMillis);

  //   stepper.enableOutputs();
  //   Serial.print("Next move to: ");
  //   Serial.println(positions[i]);
  //   // stepper.moveTo(positions[i]);
  //   stepper.move(positions[i]);


  //   Serial.print("Current position: ");
  //   Serial.println(stepper.currentPosition());
  //   // stepper.runToNewPosition(positions[i]);
  //   stepper.runToPosition();

    
  //   Serial.print("In position: ");
  //   Serial.println(stepper.currentPosition());
  //   stepper.disableOutputs();
  //   delay(intervalMillis);
  }
  // Serial.println("Done");
  // Serial.println(stepper.currentPosition());
}

void loop() {}
