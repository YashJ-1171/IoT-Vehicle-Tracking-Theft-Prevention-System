"""
🚗 IoT Vehicle Tracking & Theft Prevention System - Master Entry Point
======================================================================
This script orchestrates the full IoT system simulation, interactive web dashboard,
and automated report generation.

Author: IoT & Embedded Systems Engineering Team
License: MIT
"""

import sys
import os
import argparse
import time
import threading
import subprocess

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure project root is in system path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

def print_header():
    print("=" * 70)
    print(" [SYSTEM] IoT VEHICLE TRACKING & THEFT PREVENTION SYSTEM - MASTER CLI")
    print("=" * 70)
    print(" 1. Hardware Firmware: arduino_code/vehicle_tracker_esp32.ino")
    print(" 2. Python Simulation: python_simulation/gps_simulator.py")
    print(" 3. Web Dashboard:     dashboard/app.py (http://127.0.0.1:5000)")
    print(" 4. Report Generator:  reports/report_generator.py")
    print("=" * 70)

def run_dashboard():
    """Starts the Flask interactive web dashboard."""
    print("\n[DASHBOARD] Launching Interactive Web Dashboard on port 5000...")
    from dashboard.app import app
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def run_simulation(scenario="normal", steps=20, delay=1.0):
    """Runs the virtual GPS telemetry simulator."""
    print(f"\n[SIMULATION] Starting virtual vehicle trajectory simulation (Scenario: {scenario.upper()})...")
    from python_simulation.gps_simulator import GPSSimulator
    sim = GPSSimulator(scenario=scenario, delay=delay)
    sim.run(max_steps=steps)

def generate_reports():
    """Generates PDF and CSV audit reports from telemetry history."""
    print("\n[REPORTS] Compiling Location History & Theft Audit Reports...")
    from reports.report_generator import generate_audit_reports
    generate_audit_reports()

def run_automated_test():
    """Runs an automated end-to-end verification suite."""
    print("\n[TEST SUITE] Executing End-to-End System Verification...")
    from python_simulation.gps_simulator import GPSSimulator
    from reports.report_generator import generate_audit_reports
    
    # 1. Run simulation in all 4 states briefly
    scenarios = ["normal", "parked", "theft", "geofence"]
    for sc in scenarios:
        print(f"\n--- Testing Scenario: {sc.upper()} ---")
        sim = GPSSimulator(scenario=sc, delay=0.1)
        sim.run(max_steps=5)
    
    # 2. Generate reports based on test data
    generate_audit_reports()
    print("\n[SUCCESS] End-to-End automated test completed successfully!")

def main():
    parser = argparse.ArgumentParser(description="IoT Vehicle Tracking & Theft Prevention System")
    parser.add_argument("--mode", choices=["dashboard", "sim", "report", "test", "all"], default=None,
                        help="Operation mode to launch")
    parser.add_argument("--scenario", choices=["normal", "parked", "theft", "geofence"], default="normal",
                        help="Simulation scenario (for sim mode)")
    parser.add_argument("--steps", type=int, default=30, help="Number of simulation steps")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between simulation telemetry ticks (seconds)")
    
    args = parser.parse_args()
    print_header()
    
    if args.mode == "test":
        run_automated_test()
    elif args.mode == "sim":
        run_simulation(scenario=args.scenario, steps=args.steps, delay=args.delay)
    elif args.mode == "dashboard":
        run_dashboard()
    elif args.mode == "report":
        generate_reports()
    elif args.mode == "all":
        # Run dashboard in background thread, and simulation in foreground
        dash_thread = threading.Thread(target=run_dashboard, daemon=True)
        dash_thread.start()
        time.sleep(2.0) # wait for server startup
        run_simulation(scenario=args.scenario, steps=args.steps, delay=args.delay)
        generate_reports()
    else:
        # Interactive CLI menu
        while True:
            print("\nSelect an Option:")
            print("  [1] Launch Interactive Web Dashboard (Live Tracking & Map)")
            print("  [2] Run Virtual GPS Simulation (Normal Driving)")
            print("  [3] Run Virtual GPS Simulation (Theft Attempt Detected)")
            print("  [4] Run Virtual GPS Simulation (Geofence Breach Alert)")
            print("  [5] Generate PDF & CSV Location Audit Reports")
            print("  [6] Run Complete Automated System Verification Test")
            print("  [0] Exit")
            choice = input("\nEnter choice (0-6): ").strip()
            if choice == "1":
                run_dashboard()
                break
            elif choice == "2":
                run_simulation(scenario="normal", steps=25, delay=1.0)
            elif choice == "3":
                run_simulation(scenario="theft", steps=20, delay=1.0)
            elif choice == "4":
                run_simulation(scenario="geofence", steps=20, delay=1.0)
            elif choice == "5":
                generate_reports()
            elif choice == "6":
                run_automated_test()
            elif choice == "0":
                print("\nExiting IoT Vehicle Tracking System. Goodbye!")
                break
            else:
                print("Invalid selection. Please try again.")

if __name__ == "__main__":
    main()
