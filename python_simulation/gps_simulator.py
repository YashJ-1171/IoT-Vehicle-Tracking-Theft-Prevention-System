"""
🛰️ Virtual GPS & Vehicle Telemetry Simulator Engine
=====================================================
Simulates NEO-6M GPS receiver coordinates, vehicle movement, parking jitter,
theft detection algorithms, and geofence evaluation without requiring physical hardware.
Streams real-time JSON telemetry to local web dashboard and CSV audit logs.
"""

import time
import datetime
import csv
import os
import random
import json
try:
    import urllib.request
    import urllib.error
except ImportError:
    pass

from python_simulation.geofence_engine import GeofenceEngine

if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    LOG_DIR = "/tmp"
    LOG_FILE = "/tmp/vehicle_log.csv"
else:
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    LOG_FILE = os.path.join(LOG_DIR, "vehicle_log.csv")

class GPSSimulator:
    def __init__(self, scenario="normal", delay=1.0, dashboard_url="http://127.0.0.1:5000/api/telemetry"):
        """
        Initialize Simulator with scenario profile:
          - 'normal': Regular driving within city limits.
          - 'parked': Vehicle stationary and armed with minor GPS satellite jitter.
          - 'theft': Vehicle armed, but sudden displacement occurs (unauthorized movement).
          - 'geofence': Vehicle travels outward until crossing the geofence boundary.
        """
        self.scenario = scenario.lower()
        self.delay = delay
        self.dashboard_url = dashboard_url

        # Ensure data directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        self.init_csv_log()

        # Origin point (e.g., Connaught Place, New Delhi)
        self.start_lat = 28.6139
        self.start_lng = 77.2090
        self.geofence = GeofenceEngine(center_lat=self.start_lat, center_lng=self.start_lng, radius_meters=500.0)

        # Vehicle State Variables
        self.current_lat = self.start_lat
        self.current_lng = self.start_lng
        self.speed_kmh = 0.0
        self.is_armed = False
        self.ignition_on = True
        self.relay_engine_cut = False
        self.buzzer_alarm = False
        self.alert_type = "NONE"
        self.status_text = "NORMAL"

        # Setup scenario starting conditions
        self.setup_scenario()

    def init_csv_log(self):
        """Creates CSV log header if file doesn't exist."""
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp", "Latitude", "Longitude", "Speed_KMH",
                    "Distance_To_Center_M", "Ignition_Status", "Armed_Status",
                    "System_Status", "Alert_Type", "Google_Maps_URL"
                ])

    def setup_scenario(self):
        """Configure initial variables based on scenario selection."""
        if self.scenario == "parked":
            self.is_armed = True
            self.ignition_on = False
            self.speed_kmh = 0.0
            self.status_text = "ARMED (PARKED)"
        elif self.scenario == "theft":
            self.is_armed = True
            self.ignition_on = False
            self.speed_kmh = 0.0
            self.status_text = "ARMED (PARKED)"
        elif self.scenario == "geofence":
            self.is_armed = False
            self.ignition_on = True
            self.speed_kmh = 45.0
            self.status_text = "NORMAL"
        else: # normal
            self.is_armed = False
            self.ignition_on = True
            self.speed_kmh = 35.0
            self.status_text = "NORMAL"

    def step_simulation(self, step_idx):
        """Advance simulation time and calculate next coordinates."""
        if self.scenario == "normal":
            # Driving northeast smoothly
            self.current_lat += 0.0003
            self.current_lng += 0.0003
            self.speed_kmh = random.uniform(30.0, 50.0)
            self.alert_type = "NONE"
            self.status_text = "NORMAL"

        elif self.scenario == "parked":
            # Stationary with minor GPS jitter (+/- ~3 meters)
            self.current_lat = self.start_lat + random.uniform(-0.00003, 0.00003)
            self.current_lng = self.start_lng + random.uniform(-0.00003, 0.00003)
            self.speed_kmh = 0.0
            self.alert_type = "NONE"
            self.status_text = "ARMED (PARKED)"

        elif self.scenario == "theft":
            if step_idx < 4:
                # First few steps stationary & armed
                self.speed_kmh = 0.0
                self.alert_type = "NONE"
                self.status_text = "ARMED (PARKED)"
            else:
                # Step 4+: Sudden movement while armed! (Hotwire or Towing)
                self.current_lat += 0.0008
                self.current_lng += 0.0008
                self.speed_kmh = random.uniform(25.0, 45.0)
                
                # Evaluate Theft Logic: Movement (> 0.0002 deg displacement or speed > 5 kmh) while Armed
                if self.is_armed and self.speed_kmh > 5.0:
                    self.alert_type = "THEFT_DETECTED"
                    self.status_text = "[ALERT] THEFT DETECTED (UNAUTHORIZED MOVEMENT)"
                    self.buzzer_alarm = True
                    self.relay_engine_cut = True

        elif self.scenario == "geofence":
            # Moving rapidly outward
            self.current_lat += 0.0007
            self.current_lng += 0.0007
            self.speed_kmh = 55.0

        # Evaluate Geofence Engine
        gf_result = self.geofence.check_geofence(self.current_lat, self.current_lng)
        distance_m = gf_result["distance_meters"]

        if not gf_result["is_inside"] and self.alert_type != "THEFT_DETECTED":
            self.alert_type = "GEOFENCE_BREACH"
            self.status_text = f"[WARN] GEOFENCE ALERT (Distance: {distance_m}m > {gf_result['radius_meters']}m)"
            self.buzzer_alarm = True

        return distance_m

    def generate_maps_url(self):
        """Generates Google Maps direct tracking URL."""
        return f"https://www.google.com/maps?q={self.current_lat:.6f},{self.current_lng:.6f}"

    def log_to_csv(self, timestamp_str, distance_m, maps_url):
        """Append telemetry row to CSV log."""
        with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp_str, round(self.current_lat, 6), round(self.current_lng, 6),
                round(self.speed_kmh, 1), round(distance_m, 1),
                "ON" if self.ignition_on else "OFF",
                "ARMED" if self.is_armed else "DISARMED",
                self.status_text, self.alert_type, maps_url
            ])

    def send_to_dashboard(self, payload):
        """Stream telemetry JSON payload to Flask Web Dashboard."""
        try:
            req = urllib.request.Request(
                self.dashboard_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                pass
        except Exception:
            # Dashboard server might not be running or busy; ignore silently during simulation
            pass

    def run(self, max_steps=20):
        """Run telemetry simulation loop."""
        print(f"\n[SIM] Starting Simulation Profile: [{self.scenario.upper()}]")
        print(f"Safe Geofence Origin: ({self.start_lat}, {self.start_lng}) | Radius: {self.geofence.radius_meters}m")
        print("-" * 80)
        print(f"{'STEP':<5} | {'LATITUDE':<10} | {'LONGITUDE':<10} | {'SPEED':<7} | {'DIST(m)':<8} | {'STATUS / ALERT'}")
        print("-" * 80)

        for step in range(1, max_steps + 1):
            dist_m = self.step_simulation(step)
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            maps_url = self.generate_maps_url()

            # Console Output
            print(f"{step:<5} | {self.current_lat:<10.6f} | {self.current_lng:<10.6f} | {self.speed_kmh:<7.1f} | {dist_m:<8.1f} | {self.status_text}")

            # Log to file
            self.log_to_csv(now_str, dist_m, maps_url)

            # Build telemetry packet
            telemetry_packet = {
                "timestamp": now_str,
                "latitude": round(self.current_lat, 6),
                "longitude": round(self.current_lng, 6),
                "speed_kmh": round(self.speed_kmh, 1),
                "distance_meters": round(dist_m, 1),
                "radius_meters": self.geofence.radius_meters,
                "is_armed": self.is_armed,
                "ignition_on": self.ignition_on,
                "relay_cut": self.relay_engine_cut,
                "buzzer_alarm": self.buzzer_alarm,
                "alert_type": self.alert_type,
                "status": self.status_text,
                "maps_url": maps_url
            }

            self.send_to_dashboard(telemetry_packet)
            time.sleep(self.delay)

        print("-" * 80)
        print(f"[OK] Simulation completed! Telemetry recorded in: {LOG_FILE}\n")
