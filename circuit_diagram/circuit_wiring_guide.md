# ⚡ Circuit Diagram & Hardware Assembly Guide

This document details the exact hardware pin mappings, wiring schematics, and electronic design considerations for assembling the physical **IoT Vehicle Tracking & Theft Prevention System** using an **ESP32 DevKit V1**.

---

## 📌 Complete Pinout Table

| Component | Component Pin | ESP32 Pin | Wire Color Code | Operating Voltage | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **NEO-6M GPS Module** | VCC | 3.3V / 5V | Red | 3.3V - 5V | Power supply |
| **NEO-6M GPS Module** | GND | GND | Black | 0V | Common ground |
| **NEO-6M GPS Module** | TX | **GPIO 16 (RX2)** | Blue | 3.3V UART | GPS transmits NMEA to ESP32 |
| **NEO-6M GPS Module** | RX | **GPIO 17 (TX2)** | Green | 3.3V UART | Optional configuration commands |
| **Active Piezo Buzzer** | (+) Anode | **GPIO 25** | Yellow | 3.3V Logic | Driven high during alarm states |
| **Active Piezo Buzzer** | (-) Cathode | GND | Black | 0V | Connect to common ground |
| **Status LED (Green)**| Anode (+) | **GPIO 26** | Green | 3.3V (via 220Ω)| Illuminated during normal/armed OK state |
| **Status LED (Red)** | Anode (+) | **GPIO 27** | Red | 3.3V (via 220Ω)| Flashes during theft/geofence breach |
| **5V Relay Module** | IN (Signal) | **GPIO 33** | Orange | 3.3V Logic | Controls engine immobilizer cutoff |
| **5V Relay Module** | VCC | VIN / 5V | Red | 5V | Connect to external 5V regulated rail |
| **5V Relay Module** | GND | GND | Black | 0V | Common ground |

---

## 📐 Circuit Schematic Diagram (ASCII Architecture)

```
                       +----------------------------------+
                       |        ESP32 DEVKIT V1           |
                       |                                  |
                       |      VIN (5V) [Red] ------------+---> To Relay VCC & Battery (+)
                       |      GND      [Black] ----------+---> Common Ground Rail (-)
                       |      3V3      [Red] ------------+---> To GPS VCC
                       |                                  |
 [NEO-6M GPS MODULE]   |                                  |
       TX (Blue) ----->| GPIO 16 (RX2)                    |
       RX (Green) <----| GPIO 17 (TX2)                    |
                       |                                  |
 [ACTIVE BUZZER]       |                                  |
       (+) Yellow ---->| GPIO 25                          |
                       |                                  |
 [STATUS LEDS]         |                                  |
   Green Anode (+)---> | GPIO 26 [via 220 Resistor]       |
   Red Anode   (+)---> | GPIO 27 [via 220 Resistor]       |
                       |                                  |
 [ENGINE RELAY]        |                                  |
    IN (Orange) ------>| GPIO 33                          |
                       +----------------------------------+
                                        |
                            +-----------v-----------+
                            | 5V 1-Channel Relay    |
                            | NO (Normally Open)    |---> To Vehicle Ignition Circuit Cutoff
                            | COM (Common)          |---> To Vehicle Ignition Key / Switch
                            +-----------------------+
```

---

## 🔧 Component Connection Explanations & Electronic Best Practices

1. **NEO-6M GPS UART Interface**:
   - The NEO-6M communicates via standard asynchronous serial (UART) at `9600` baud.
   - We connect GPS `TX` to ESP32 `GPIO 16 (RX2)` because the hardware serial engine on UART2 offers buffered DMA reception, preventing dropped NMEA characters even under heavy WiFi load.

2. **Relay Isolation & Engine Immobilizer Safety**:
   - Vehicle ignition circuits carry $12\text{V}$ DC currents. A mechanical or solid-state relay module isolates the low-voltage ESP32 logic ($3.3\text{V}$) from high automotive voltages.
   - When `GPIO 33` asserts `HIGH`, the optocoupler inside the relay module switches the contacts from Normally Closed (NC) to Normally Open (NO), cutting off power to the ignition coil or starter relay safely.

3. **Power Supply & Battery Backup**:
   - To protect against thieves disconnecting the main car battery ($12\text{V}$), the ESP32 and GPS module are powered via an uninterruptible power buck regulator attached to a backup $18650$ Li-Ion battery pack ($3.7\text{V}-4.2\text{V}$).
