/*
 * 🚗 IoT Vehicle Tracking & Theft Prevention System - Production Firmware
 * =======================================================================
 * Target Microcontroller: ESP32 DevKit V1
 * Peripherals: NEO-6M GPS Module, Active Buzzer, Dual Status LEDs, 1-Ch Relay
 * Protocols: HTTP REST POST / ThingSpeak / MQTT
 *
 * Pin Mapping:
 *   GPS RX -> ESP32 TX2 (GPIO 17)
 *   GPS TX -> ESP32 RX2 (GPIO 16)
 *   Buzzer -> GPIO 25
 *   Green LED (Normal/Armed OK) -> GPIO 26
 *   Red LED (Alarm/Theft)       -> GPIO 27
 *   Engine Cutoff Relay         -> GPIO 33
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <HardwareSerial.h>
#include <TinyGPS++.h>
#include <math.h>

// --- WiFi & Cloud Configuration ---
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL    = "http://192.168.1.100:5000/api/telemetry"; // Or ThingSpeak URL

// --- Pin Definitions ---
#define RXD2 16
#define TXD2 17
#define PIN_BUZZER 25
#define PIN_LED_GREEN 26
#define PIN_LED_RED 27
#define PIN_RELAY_CUTOFF 33

// --- Geofence Safe Origin ---
const double SAFE_CENTER_LAT = 28.613900;
const double SAFE_CENTER_LNG = 77.209000;
const double SAFE_RADIUS_METERS = 500.0;

// --- Security & System States ---
bool isArmed = true;           // System is armed (e.g. parked and locked)
bool ignitionOn = false;       // Ignition state
bool relayCut = false;
bool buzzerAlarm = false;
String alertType = "NONE";
String systemStatus = "NORMAL";

double lastLat = SAFE_CENTER_LAT;
double lastLng = SAFE_CENTER_LNG;

TinyGPSPlus gps;
HardwareSerial gpsSerial(2);

// --- Haversine Geofence Calculation in C++ ---
double calculateHaversineDistance(double lat1, double lon1, double lat2, double lon2) {
  const double R = 6371000.0; // Earth radius in meters
  double phi1 = lat1 * M_PI / 180.0;
  double phi2 = lat2 * M_PI / 180.0;
  double deltaPhi = (lat2 - lat1) * M_PI / 180.0;
  double deltaLambda = (lon2 - lon1) * M_PI / 180.0;

  double a = sin(deltaPhi / 2.0) * sin(deltaPhi / 2.0) +
             cos(phi1) * cos(phi2) * sin(deltaLambda / 2.0) * sin(deltaLambda / 2.0);
  double c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a));
  return R * c;
}

void setup() {
  Serial.begin(115200);
  gpsSerial.begin(9600, SERIAL_8N1, RXD2, TXD2);

  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);
  pinMode(PIN_RELAY_CUTOFF, OUTPUT);

  digitalWrite(PIN_BUZZER, LOW);
  digitalWrite(PIN_LED_GREEN, HIGH);
  digitalWrite(PIN_LED_RED, LOW);
  digitalWrite(PIN_RELAY_CUTOFF, LOW); // Normal engine operation

  Serial.println("==============================================");
  Serial.println("🚗 ESP32 Vehicle Tracking & Security Initialized");
  Serial.println("==============================================");

  // Connect to WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 15) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi Connected! IP Address: " + WiFi.localIP().toString());
  } else {
    Serial.println("\n⚠️ WiFi connection failed. Operating in Offline / Hardware Alarm Mode.");
  }
}

void evaluateSecurityState(double currentLat, double currentLng, double speedKmh, double distToCenter) {
  alertType = "NONE";
  systemStatus = isArmed ? "ARMED (PARKED)" : "NORMAL DRIVING";
  buzzerAlarm = false;

  // 1. Check Geofence Breach
  if (distToCenter > SAFE_RADIUS_METERS) {
    alertType = "GEOFENCE_BREACH";
    systemStatus = "⚠️ GEOFENCE EXITED (" + String(distToCenter, 1) + "m)";
    buzzerAlarm = true;
  }

  // 2. Check Theft Condition (Movement detected while Armed)
  double displacementFromParked = calculateHaversineDistance(lastLat, lastLng, currentLat, currentLng);
  if (isArmed && (speedKmh > 5.0 || displacementFromParked > 15.0)) {
    alertType = "THEFT_DETECTED";
    systemStatus = "🚨 THEFT ALERT! UNAUTHORIZED DISPLACEMENT";
    buzzerAlarm = true;
    relayCut = true; // Actuate engine immobilizer cut-off
  }

  // Actuate Hardware Pins
  digitalWrite(PIN_BUZZER, buzzerAlarm ? HIGH : LOW);
  digitalWrite(PIN_LED_RED, buzzerAlarm ? HIGH : LOW);
  digitalWrite(PIN_LED_GREEN, buzzerAlarm ? LOW : HIGH);
  digitalWrite(PIN_RELAY_CUTOFF, relayCut ? HIGH : LOW);
}

void sendCloudTelemetry(double lat, double lng, double speed, double dist) {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  String jsonPayload = "{";
  jsonPayload += "\"latitude\": " + String(lat, 6) + ",";
  jsonPayload += "\"longitude\": " + String(lng, 6) + ",";
  jsonPayload += "\"speed_kmh\": " + String(speed, 1) + ",";
  jsonPayload += "\"distance_meters\": " + String(dist, 1) + ",";
  jsonPayload += "\"is_armed\": " + String(isArmed ? "true" : "false") + ",";
  jsonPayload += "\"ignition_on\": " + String(ignitionOn ? "true" : "false") + ",";
  jsonPayload += "\"relay_cut\": " + String(relayCut ? "true" : "false") + ",";
  jsonPayload += "\"buzzer_alarm\": " + String(buzzerAlarm ? "true" : "false") + ",";
  jsonPayload += "\"alert_type\": \"" + alertType + "\",";
  jsonPayload += "\"status\": \"" + systemStatus + "\",";
  jsonPayload += "\"maps_url\": \"https://www.google.com/maps?q=" + String(lat, 6) + "," + String(lng, 6) + "\"";
  jsonPayload += "}";

  int httpCode = http.POST(jsonPayload);
  if (httpCode > 0) {
    Serial.printf("🌐 Telemetry POST success: HTTP %d\n", httpCode);
  } else {
    Serial.printf("⚠️ Telemetry POST failed: error %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();
}

void loop() {
  // Read NMEA sentences from NEO-6M GPS receiver over UART2
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }

  // Process telemetry every 2 seconds
  static unsigned long lastSend = 0;
  if (millis() - lastSend > 2000) {
    lastSend = millis();

    double currentLat = gps.location.isValid() ? gps.location.lat() : SAFE_CENTER_LAT;
    double currentLng = gps.location.isValid() ? gps.location.lng() : SAFE_CENTER_LNG;
    double speedKmh   = gps.speed.isValid()    ? gps.speed.kmph()   : 0.0;

    double distToCenter = calculateHaversineDistance(SAFE_CENTER_LAT, SAFE_CENTER_LNG, currentLat, currentLng);

    // Evaluate Security & Control Actuators
    evaluateSecurityState(currentLat, currentLng, speedKmh, distToCenter);

    // Serial Monitor Debug Output
    Serial.println("\n--- 📍 Vehicle Telemetry Snapshot ---");
    Serial.printf("Coordinates : %.6f, %.6f | Speed: %.1f km/h\n", currentLat, currentLng, speedKmh);
    Serial.printf("Geofence    : %.1f meters from safe center\n", distToCenter);
    Serial.println("Status      : " + systemStatus);
    Serial.println("Actuators   : Buzzer=" + String(buzzerAlarm) + " | RelayCut=" + String(relayCut));

    // Publish Telemetry Payload
    sendCloudTelemetry(currentLat, currentLng, speedKmh, distToCenter);
  }
}
