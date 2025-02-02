#include <Wire.h>
#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Arduino.h>

#define DHTPIN 4       // GPIO pin for the DHT22 sensor
#define DHTTYPE DHT22
#define ONE_WIRE_BUS 5 // GPIO pin for the DS18B20 sensor
#define PH_SENSOR_PIN 34  // ADC pin connected to pH sensor
#define NUM_SAMPLES 10    // Number of readings for averaging
const int tdsPin = 35;

float slope = -3.978;     // Calculated slope
float intercept = 17.857; // Calculated intercept

// Calibration values
const float voltageRef = 5.0; // Reference voltage (modify based on your setup, e.g., 3.3V for ESP32)
const float rawValueAt160ppm = 656; // Raw value corresponding to 160 ppm
const float voltageAt160ppm = 3.21; // Voltage corresponding to 160 ppm

DHT dht(DHTPIN, DHTTYPE);
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Function to read and average multiple analog samples
float readAverageVoltage(int pin) {
  float sum = 0.0;
  for (int i = 0; i < NUM_SAMPLES; i++) {
    sum += analogRead(pin) * 3.3 / 4095.0; // Convert ADC value to voltage
    delay(10); // Small delay between samples
  }
  return sum / NUM_SAMPLES;
}

// Function to calculate pH from raw voltage
float calculatePH(float voltage) {
  return slope * voltage + intercept;
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12); // Set ADC resolution to 12 bits
  dht.begin();
  sensors.begin();
}

void loop() {
  float phrawVoltage = readAverageVoltage(PH_SENSOR_PIN);
  float phValue = calculatePH(phrawVoltage);

  // Delay before reading other sensors to allow the pH sensor to stabilize
  delay(1000);

  // Read TDS sensor
  int rawValue = analogRead(tdsPin);
  float voltage = (rawValue / 1023.0) * voltageRef; // Convert raw value to voltage
  float tdsValue = (rawValue / rawValueAt160ppm) * 160; // Map raw value to TDS (ppm)

  // Read temperature and humidity from the DHT22 sensor
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  // Request water temperature from the DS18B20 sensor
  sensors.requestTemperatures();
  float waterTemp = sensors.getTempCByIndex(0);

  // Print other sensor readings
  if (isnan(temp) || isnan(hum) || waterTemp == DEVICE_DISCONNECTED_C) {
    Serial.println("Error reading sensors");
  } else {
    Serial.print("pH Value: ");
    Serial.println(phValue, 2);
    Serial.printf("Air Temp: %.2f°C\n", temp);
    Serial.printf("Humidity: %.2f%%\n", hum);
    Serial.printf("Water Temp: %.2f°C\n", waterTemp);
    Serial.printf("TDS: %.1f ppm\n", tdsValue);
    Serial.println("------------------------------");
  }

  delay(1000);
}

// Average value from a given pin
int readAverage(int pin, int samples) {
  long sum = 0;
  for (int i = 0; i < samples; i++) {
    sum += analogRead(pin);
    delay(10); // Short delay between readings to reduce noise
  }
  return sum / samples;
}
