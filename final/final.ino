#include <MsTimer2.h>
#include <Servo.h>

// define pins for sensors
#define SOIL_SENSOR 0
#define LIQUID_LEVEL_SENSOR 2

// declare global variables
Servo servo;
int waterLevel;
int soilMoisture;
bool waterPlant = false;
String data;

void setup() {
  // set baud rate to 57600
  Serial.begin(57600);
  // declare sensors as input
  pinMode(SOIL_SENSOR, INPUT);
  pinMode(LIQUID_LEVEL_SENSOR, INPUT);
  // attach servo to pin and set initial position to 0
  servo.attach(9);
  servo.write(0);
  // set timer to call readSoilMoisture every 5000ms
  MsTimer2::set(5000, readSoilMoisture);
  MsTimer2::start();
}

void loop() { 
  // if the waterPlant flag is true
  if (waterPlant) {
    // move servo 90 degrees to the right
    for (int i = 0; i < 90; i++) {
      servo.write(i);
      delay(15);  
    }
    // then move servo back to upright position
    for (int j = 90; j > 0; j--) {
      servo.write(j);
      delay(15);
    }
    // retoggle the flag back to false
    waterPlant = false;
  }
}

void readSoilMoisture() {
  // read from soil sensor
  soilMoisture = analogRead(SOIL_SENSOR);
  // read from liquid level sensor
  waterLevel = digitalRead(LIQUID_LEVEL_SENSOR);
  // if waterLevel equals 1 that means water is not touching the sensor
  if (waterLevel == 1) {
    // create string consisting of soilMoisture value and 'e' for empty
    data = String(soilMoisture) + 'e';
  } else {
    // else the waterLevel equals 0 which means water is touching the sensor
    // create string consisting of soilMoisture value and 'f' for full
    data = String(soilMoisture) + 'f';
  }
  // send data to base station
  Serial.println(data);
  // if soil moisture is less than 850 and waterLevel is 0 (water is available in container)
  if (soilMoisture < 850 && waterLevel == 0) {
    // toggle the waterPlant flag to true
    waterPlant = true;
  }
}

