"""
🌐 Interactive Web Dashboard - Flask Backend API
==============================================
Serves real-time telemetry updates, live Leaflet maps, geofence radius display,
and historical data analytics for the IoT Vehicle Tracking & Theft Prevention System.
"""

import os
import csv
import json
import subprocess
import threading
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    LOG_FILE = "/tmp/vehicle_log.csv"
else:
    LOG_FILE = os.path.join(PROJECT_ROOT, "data", "vehicle_log.csv")

# In-memory current vehicle state
latest_telemetry = {
    "timestamp": "N/A",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "speed_kmh": 0.0,
    "distance_meters": 0.0,
    "radius_meters": 500.0,
    "is_armed": False,
    "ignition_on": True,
    "relay_cut": False,
    "buzzer_alarm": False,
    "alert_type": "NONE",
    "status": "SYSTEM IDLE / WAITING FOR TELEMETRY",
    "maps_url": "https://www.google.com/maps?q=28.6139,77.2090"
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/telemetry", methods=["GET", "POST"])
def handle_telemetry():
    global latest_telemetry
    if request.method == "POST":
        data = request.get_json(silent=True)
        if data:
            latest_telemetry.update(data)
        return jsonify({"status": "success", "received": data}), 200
    else:
        return jsonify(latest_telemetry), 200

@app.route("/api/history", methods=["GET"])
def get_history():
    """Returns recent logs from vehicle_log.csv for Chart.js and historical tables."""
    history = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                history.append(row)
    # Return last 30 data points
    return jsonify({"history": history[-30:]}), 200

@app.route("/api/control", methods=["POST"])
def control_simulation():
    """Allows triggering simulation profiles directly from the Web UI."""
    data = request.get_json(silent=True) or {}
    action = data.get("action", "normal")
    
    # Run simulation in a background daemon thread so API returns immediately
    from python_simulation.gps_simulator import GPSSimulator
    def background_sim():
        sim = GPSSimulator(scenario=action, delay=1.0)
        sim.run(max_steps=20)

    sim_thread = threading.Thread(target=background_sim, daemon=True)
    sim_thread.start()
    
    return jsonify({"status": "triggered", "scenario": action}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
