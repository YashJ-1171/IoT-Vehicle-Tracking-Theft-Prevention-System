<div align="center">

# 🚗 IoT Vehicle Tracking & Theft Prevention System

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Embedded: ESP32](https://img.shields.io/badge/Embedded-ESP32%20DevKit%20V1-success.svg)](https://www.espressif.com/en/products/socs/esp32)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-yellow.svg)](https://www.python.org/)
[![Dashboard: Flask & Leaflet](https://img.shields.io/badge/Dashboard-Flask%20%7C%20Leaflet.js-00d8ff.svg)](#)

*An industry-ready, placement-oriented full-stack IoT security platform featuring real-time GPS trajectory tracking, spherical Haversine geofence containment, automated engine immobilization logic, virtual telemetry simulation, and interactive web dashboarding.*

</div>

---

## 🌟 Overview & Problem Statement

Unmonitored vehicles and commercial logistics fleets face severe vulnerability to theft, unauthorized joyriding, fuel drainage, and route deviations. Traditional passive alarms only emit localized noise, offering zero remote tracking or intervention capabilities once a vehicle leaves the parking lot.

This project introduces a **Complete IoT Vehicle Tracking & Anti-Theft Command Center** engineered with dual-mode versatility:
1. **Physical Hardware Mode**: Ready to flash onto an **ESP32 DevKit V1** connected to a **NEO-6M GPS receiver**, active piezo buzzer, status indicators, and an optocoupler-isolated engine cut-off relay.
2. **Virtual Simulation Mode**: A robust Python telemetry engine that simulates GPS trajectories across normal driving, parking jitter, theft displacement, and geofence breaches without requiring physical hardware.

---

## ⚙️ Key Architecture & Features

- 🛰️ **High-Precision GNSS Parsing**: Reads NMEA `$GPRMC` / `$GPGGA` satellite data streams.
- 🌐 **Spherical Haversine Geofencing**: Computes real-time great-circle distance between vehicle coordinates and safe origin zones ($500\text{m}$ default radius).
- 🚨 **Automated Theft Detection & Intervention**: Triggers immediate buzzer alarms and asserts digital high on optocoupler relay pins to immobilize vehicle ignition upon unauthorized movement.
- 🖥️ **Interactive Glassmorphic Web Dashboard**: Built with Flask, Leaflet.js maps, and Chart.js analytics for live visual telemetry.
- 📊 **Automated Audit Reporting**: Generates presentation-ready PDF security audits and analytical CSV trajectory logs.

---

## 📂 Repository Structure

```
IoT-Vehicle-Tracking-Theft-Prevention-System/
│
├── arduino_code/
│   └── vehicle_tracker_esp32.ino   # Complete production C++ ESP32 firmware
├── python_simulation/
│   ├── geofence_engine.py          # Spherical Haversine mathematical model
│   └── gps_simulator.py            # Multi-profile virtual GPS telemetry generator
├── dashboard/
│   ├── app.py                      # Flask REST API & Web Server
│   ├── static/                     # Premium glassmorphic CSS & Leaflet JS logic
│   └── templates/                  # Interactive HTML dashboard layout
├── circuit_diagram/
│   ├── circuit_wiring_guide.md     # Detailed hardware schematic & wiring instructions
│   └── pinout_table.csv            # Pin mapping quick reference
├── reports/
│   └── report_generator.py         # ReportLab PDF & CSV audit document compiler
├── docs/
│   ├── ARCHITECTURE.md             # Detailed system architecture breakdown
│   ├── INTERVIEW_PREP.md           # 10 High-impact placement interview questions & answers
│   └── GITHUB_STRATEGY.md          # Best practices for portfolio showcasing
├── main.py                         # Master orchestration entry CLI
└── requirements.txt                # Python package dependencies
```

---

## 🚀 Setup & Execution Guide

### 1️⃣ Prerequisite Environment
Ensure Python 3.9+ is installed on your Windows, Linux, or macOS system. Install required Python packages:

```powershell
pip install -r requirements.txt
```

### 2️⃣ Launching the Interactive Web Dashboard (Local)
Start the live command center server:

```powershell
python main.py --mode dashboard
```
Open your web browser and navigate to: **`http://127.0.0.1:5000`**

### 🌐 Cloud Deployment (Vercel Serverless)
This project is pre-configured with `vercel.json` and `api/index.py` for instant serverless cloud deployment!
To deploy directly from your terminal using Vercel CLI:
```powershell
npx vercel --prod
```

### 3️⃣ Running Virtual Simulation Scenarios
Open a second terminal window and run the simulator in your desired test profile:

```powershell
# Simulate normal city driving
python main.py --mode sim --scenario normal

# Simulate unauthorized towing / hotwire theft attempt
python main.py --mode sim --scenario theft

# Simulate boundary breach outside 500m safe radius
python main.py --mode sim --scenario geofence
```

### 4️⃣ Generating Audit Reports (PDF & CSV)
Compile formatted analytical logs and presentation PDFs:

```powershell
python main.py --mode report
```
Inspect generated outputs inside the `outputs/` folder!

---

## 🖥️ Command Center Dashboard Preview

When active, the dashboard provides:
- Live Leaflet map centering on current vehicle marker with translucent blue geofence overlay.
- Real-time speedometer and distance gauge.
- Hardware Actuator status cards showing Ignition state, Piezo Alarm status, and Relay Engine Cutoff status.
- Direct **Open Google Maps ↗** button to generate shareable navigation coordinates.

---

## 🔮 Future Enhancements

- **Cellular Triangulation (LBS)**: Integrating SIM800L GSM fallback positioning when underground tunnels block GNSS satellite line-of-sight.
- **OBD-II CAN Bus Interface**: Reading engine RPM, coolant temperature, and fuel level directly from the vehicle engine control unit via ELM327 Bluetooth.
- **Machine Learning Anomaly Detection**: Training Isolation Forests to predict erratic driving or hijacking patterns before physical geofence boundaries are breached.

---

<div align="center">
<b>Built for IoT Engineering & Campus Placements</b>
</div>
