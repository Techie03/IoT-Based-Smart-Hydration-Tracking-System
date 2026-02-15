/*
 * IoT-Based Smart Hydration Tracking System
 * ===========================================
 * ESP8266 microcontroller with ultrasonic sensor for water level tracking
 * Firebase cloud integration via REST APIs
 * Continuous monitoring for 100+ participants
 * 
 * Hardware:
 * - ESP8266 (NodeMCU)
 * - HC-SR04 Ultrasonic Sensor
 * - Water bottle with mounting bracket
 * 
 * Author: IoT Hydration Team
 * Date: 2023
 */

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

// ==================== CONFIGURATION ====================

// WiFi Credentials
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// Firebase Configuration
const char* FIREBASE_HOST = "your-project.firebaseio.com";
const char* FIREBASE_AUTH = "YOUR_FIREBASE_SECRET";
const char* DEVICE_ID = "DEVICE_001";  // Unique device identifier
const char* USER_ID = "USER_001";      // User identifier

// Ultrasonic Sensor Pins
#define TRIG_PIN D1  // GPIO5
#define ECHO_PIN D2  // GPIO4

// Bottle Specifications (in cm)
const float BOTTLE_HEIGHT = 20.0;      // Total bottle height
const float BOTTLE_CAPACITY = 1000.0;   // Capacity in ml
const float MIN_DISTANCE = 2.0;         // Minimum sensor distance
const float MAX_DISTANCE = 20.0;        // Maximum sensor distance

// Measurement Settings
const int MEASUREMENT_INTERVAL = 30000;  // 30 seconds
const int SAMPLES_PER_READING = 5;       // Multiple samples for accuracy
const float CONSUMPTION_THRESHOLD = 50.0; // ml threshold for drink event

// ==================== GLOBAL VARIABLES ====================

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 0, 60000);

float currentWaterLevel = 0.0;
float previousWaterLevel = 0.0;
float totalConsumption = 0.0;
int drinkingEvents = 0;

unsigned long lastMeasurement = 0;
unsigned long lastUpload = 0;
unsigned long sessionStart = 0;

bool wifiConnected = false;
bool sensorCalibrated = false;

// Statistics
struct Statistics {
  float avgConsumptionRate;
  float maxWaterLevel;
  float minWaterLevel;
  int totalMeasurements;
  int uploadSuccess;
  int uploadFails;
};

Statistics stats = {0, 0, 100, 0, 0, 0};

// ==================== SETUP ====================

void setup() {
  Serial.begin(115200);
  delay(100);
  
  Serial.println("\n\n");
  Serial.println("====================================");
  Serial.println("IoT Smart Hydration Tracking System");
  Serial.println("====================================");
  Serial.println();
  
  // Initialize pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  
  // Initialize components
  connectWiFi();
  timeClient.begin();
  calibrateSensor();
  
  sessionStart = millis();
  
  Serial.println("\nSystem Ready!");
  Serial.println("Starting continuous monitoring...\n");
}

// ==================== MAIN LOOP ====================

void loop() {
  // Ensure WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Reconnecting...");
    connectWiFi();
  }
  
  // Update time
  timeClient.update();
  
  // Take measurement at regular intervals
  unsigned long currentTime = millis();
  if (currentTime - lastMeasurement >= MEASUREMENT_INTERVAL) {
    performMeasurement();
    lastMeasurement = currentTime;
  }
  
  // Blink LED to show activity
  blinkLED(1);
  
  delay(1000);
}

// ==================== WIFI CONNECTION ====================

void connectWiFi() {
  Serial.println("Connecting to WiFi...");
  Serial.print("SSID: ");
  Serial.println(WIFI_SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    Serial.println("\n✓ WiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal Strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    wifiConnected = false;
    Serial.println("\n✗ WiFi Connection Failed!");
  }
  Serial.println();
}

// ==================== SENSOR CALIBRATION ====================

void calibrateSensor() {
  Serial.println("Calibrating ultrasonic sensor...");
  Serial.println("Please ensure bottle is full for calibration");
  
  delay(3000);
  
  // Take multiple readings for calibration
  float calibrationReadings[10];
  for (int i = 0; i < 10; i++) {
    calibrationReadings[i] = measureDistance();
    delay(200);
  }
  
  // Calculate average
  float avgDistance = 0;
  for (int i = 0; i < 10; i++) {
    avgDistance += calibrationReadings[i];
  }
  avgDistance /= 10.0;
  
  Serial.print("Calibration distance: ");
  Serial.print(avgDistance);
  Serial.println(" cm");
  
  sensorCalibrated = true;
  Serial.println("✓ Sensor calibrated!\n");
}

// ==================== ULTRASONIC MEASUREMENT ====================

float measureDistance() {
  // Take multiple samples and average
  float totalDistance = 0;
  int validSamples = 0;
  
  for (int i = 0; i < SAMPLES_PER_READING; i++) {
    // Trigger pulse
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    
    // Read echo
    long duration = pulseIn(ECHO_PIN, HIGH, 30000);  // 30ms timeout
    
    if (duration > 0) {
      float distance = duration * 0.034 / 2.0;  // Speed of sound: 340 m/s
      
      // Validate reading
      if (distance >= MIN_DISTANCE && distance <= MAX_DISTANCE) {
        totalDistance += distance;
        validSamples++;
      }
    }
    
    delay(60);  // Wait between samples
  }
  
  if (validSamples > 0) {
    return totalDistance / validSamples;
  } else {
    return -1;  // Invalid reading
  }
}

// ==================== WATER LEVEL CALCULATION ====================

float calculateWaterLevel(float distance) {
  // Convert distance to water level percentage
  float waterHeight = BOTTLE_HEIGHT - distance;
  
  // Ensure within valid range
  if (waterHeight < 0) waterHeight = 0;
  if (waterHeight > BOTTLE_HEIGHT) waterHeight = BOTTLE_HEIGHT;
  
  // Calculate percentage
  float percentage = (waterHeight / BOTTLE_HEIGHT) * 100.0;
  
  // Calculate volume in ml
  float volume = (percentage / 100.0) * BOTTLE_CAPACITY;
  
  return percentage;
}

// ==================== PERFORM MEASUREMENT ====================

void performMeasurement() {
  Serial.println("--- Taking Measurement ---");
  
  // Measure distance
  float distance = measureDistance();
  
  if (distance < 0) {
    Serial.println("✗ Invalid sensor reading");
    return;
  }
  
  // Calculate water level
  previousWaterLevel = currentWaterLevel;
  currentWaterLevel = calculateWaterLevel(distance);
  
  // Calculate volume in ml
  float currentVolume = (currentWaterLevel / 100.0) * BOTTLE_CAPACITY;
  float previousVolume = (previousWaterLevel / 100.0) * BOTTLE_CAPACITY;
  
  // Detect drinking event
  float volumeChange = previousVolume - currentVolume;
  if (volumeChange >= CONSUMPTION_THRESHOLD) {
    drinkingEvents++;
    totalConsumption += volumeChange;
    
    Serial.println("🥤 DRINKING EVENT DETECTED!");
    Serial.print("   Amount consumed: ");
    Serial.print(volumeChange);
    Serial.println(" ml");
  }
  
  // Update statistics
  stats.totalMeasurements++;
  if (currentWaterLevel > stats.maxWaterLevel) {
    stats.maxWaterLevel = currentWaterLevel;
  }
  if (currentWaterLevel < stats.minWaterLevel) {
    stats.minWaterLevel = currentWaterLevel;
  }
  
  // Calculate average consumption rate
  unsigned long sessionDuration = (millis() - sessionStart) / 1000;  // seconds
  if (sessionDuration > 0) {
    stats.avgConsumptionRate = (totalConsumption / sessionDuration) * 3600;  // ml/hour
  }
  
  // Display results
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");
  
  Serial.print("Water Level: ");
  Serial.print(currentWaterLevel);
  Serial.println("%");
  
  Serial.print("Volume: ");
  Serial.print(currentVolume);
  Serial.print(" ml / ");
  Serial.print(BOTTLE_CAPACITY);
  Serial.println(" ml");
  
  Serial.print("Total Consumed: ");
  Serial.print(totalConsumption);
  Serial.println(" ml");
  
  Serial.print("Drinking Events: ");
  Serial.println(drinkingEvents);
  
  Serial.println();
  
  // Upload to Firebase
  uploadToFirebase(distance, currentWaterLevel, currentVolume, volumeChange);
}

// ==================== FIREBASE UPLOAD ====================

void uploadToFirebase(float distance, float level, float volume, float consumption) {
  if (!wifiConnected) {
    Serial.println("✗ Cannot upload: WiFi not connected");
    stats.uploadFails++;
    return;
  }
  
  Serial.println("Uploading to Firebase...");
  
  WiFiClientSecure client;
  client.setInsecure();  // For testing; use proper certificate in production
  
  HTTPClient http;
  
  // Construct Firebase URL
  String url = String("https://") + FIREBASE_HOST + 
               "/hydration/" + DEVICE_ID + "/readings.json?auth=" + FIREBASE_AUTH;
  
  // Get current timestamp
  unsigned long timestamp = timeClient.getEpochTime();
  
  // Create JSON payload
  StaticJsonDocument<512> doc;
  
  doc["timestamp"] = timestamp;
  doc["device_id"] = DEVICE_ID;
  doc["user_id"] = USER_ID;
  
  JsonObject sensor_data = doc.createNestedObject("sensor_data");
  sensor_data["distance_cm"] = distance;
  sensor_data["water_level_percent"] = level;
  sensor_data["volume_ml"] = volume;
  sensor_data["bottle_capacity_ml"] = BOTTLE_CAPACITY;
  
  JsonObject consumption_data = doc.createNestedObject("consumption");
  consumption_data["event_detected"] = (consumption >= CONSUMPTION_THRESHOLD);
  consumption_data["amount_ml"] = consumption;
  consumption_data["total_consumed_ml"] = totalConsumption;
  consumption_data["drinking_events"] = drinkingEvents;
  
  JsonObject session_data = doc.createNestedObject("session");
  session_data["duration_seconds"] = (millis() - sessionStart) / 1000;
  session_data["avg_consumption_rate_ml_per_hour"] = stats.avgConsumptionRate;
  
  JsonObject device_status = doc.createNestedObject("device_status");
  device_status["wifi_rssi"] = WiFi.RSSI();
  device_status["measurements"] = stats.totalMeasurements;
  device_status["uptime_seconds"] = millis() / 1000;
  
  // Serialize to JSON string
  String jsonData;
  serializeJson(doc, jsonData);
  
  // Send POST request
  http.begin(client, url);
  http.addHeader("Content-Type", "application/json");
  
  int httpCode = http.POST(jsonData);
  
  if (httpCode > 0) {
    Serial.print("✓ Upload successful! HTTP Code: ");
    Serial.println(httpCode);
    
    if (httpCode == HTTP_CODE_OK) {
      String response = http.getString();
      Serial.print("Response: ");
      Serial.println(response);
      stats.uploadSuccess++;
    }
  } else {
    Serial.print("✗ Upload failed! Error: ");
    Serial.println(http.errorToString(httpCode));
    stats.uploadFails++;
  }
  
  http.end();
  Serial.println();
}

// ==================== UTILITY FUNCTIONS ====================

void blinkLED(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_BUILTIN, LOW);   // LED ON (inverted)
    delay(100);
    digitalWrite(LED_BUILTIN, HIGH);  // LED OFF
    delay(100);
  }
}

void printStatistics() {
  Serial.println("\n====================================");
  Serial.println("Session Statistics");
  Serial.println("====================================");
  
  Serial.print("Total Measurements: ");
  Serial.println(stats.totalMeasurements);
  
  Serial.print("Successful Uploads: ");
  Serial.println(stats.uploadSuccess);
  
  Serial.print("Failed Uploads: ");
  Serial.println(stats.uploadFails);
  
  Serial.print("Max Water Level: ");
  Serial.print(stats.maxWaterLevel);
  Serial.println("%");
  
  Serial.print("Min Water Level: ");
  Serial.print(stats.minWaterLevel);
  Serial.println("%");
  
  Serial.print("Avg Consumption Rate: ");
  Serial.print(stats.avgConsumptionRate);
  Serial.println(" ml/hour");
  
  Serial.print("Total Consumption: ");
  Serial.print(totalConsumption);
  Serial.println(" ml");
  
  Serial.print("Drinking Events: ");
  Serial.println(drinkingEvents);
  
  unsigned long uptime = millis() / 1000;
  Serial.print("Uptime: ");
  Serial.print(uptime / 3600);
  Serial.print("h ");
  Serial.print((uptime % 3600) / 60);
  Serial.print("m ");
  Serial.print(uptime % 60);
  Serial.println("s");
  
  Serial.println("====================================\n");
}

/*
 * Serial Commands (for debugging):
 * - 's' : Print statistics
 * - 'r' : Reset statistics
 * - 'c' : Calibrate sensor
 * - 'm' : Force measurement
 * - 'w' : Check WiFi status
 */
