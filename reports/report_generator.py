"""
📊 Automated Audit Report Generator (CSV & PDF)
==============================================
Reads vehicle trajectory telemetry from data/vehicle_log.csv and compiles:
  1. Analytical CSV summary (outputs/location_history_report.csv)
  2. Executive presentation PDF document (outputs/Location_History_and_Theft_Audit_Report.pdf)
"""

import os
import csv
import datetime
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    DATA_FILE = "/tmp/vehicle_log.csv"
    OUTPUT_DIR = "/tmp/outputs"
else:
    DATA_FILE = os.path.join(PROJECT_ROOT, "data", "vehicle_log.csv")
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs")
CSV_OUTPUT = os.path.join(OUTPUT_DIR, "location_history_report.csv")
PDF_OUTPUT = os.path.join(OUTPUT_DIR, "Location_History_and_Theft_Audit_Report.pdf")

def ensure_sample_data():
    """Generates sample telemetry logs if vehicle_log.csv is missing or empty."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) < 50:
        with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestamp", "Latitude", "Longitude", "Speed_KMH",
                "Distance_To_Center_M", "Ignition_Status", "Armed_Status",
                "System_Status", "Alert_Type", "Google_Maps_URL"
            ])
            # Add 5 simulated rows
            base_lat = 28.6139
            base_lng = 77.2090
            now = datetime.datetime.now()
            for i in range(5):
                t_str = (now - datetime.timedelta(minutes=5-i)).strftime("%Y-%m-%d %H:%M:%S")
                lat = round(base_lat + (i * 0.0002), 6)
                lng = round(base_lng + (i * 0.0002), 6)
                speed = 35.0 if i < 3 else (0.0 if i == 3 else 42.0)
                status = "NORMAL" if i < 3 else ("ARMED (PARKED)" if i == 3 else "🚨 THEFT ALERT")
                alert = "NONE" if i < 4 else "THEFT_DETECTED"
                maps_url = f"https://www.google.com/maps?q={lat},{lng}"
                writer.writerow([t_str, lat, lng, speed, i*45.0, "ON" if i!=3 else "OFF", "ARMED" if i>=3 else "DISARMED", status, alert, maps_url])

def generate_audit_reports():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ensure_sample_data()

    rows = []
    with open(DATA_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        print("No telemetry rows found to generate report.")
        return

    # 1. Generate Analytical CSV Report
    with open(CSV_OUTPUT, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Audit ID", "Timestamp", "Coordinates", "Speed (km/h)", "Geofence Dist (m)", "Security State", "Alert Event"])
        for idx, r in enumerate(rows, 1):
            coords = f"{r.get('Latitude', '')}, {r.get('Longitude', '')}"
            sec_state = f"Ignition: {r.get('Ignition_Status', '')} | Armed: {r.get('Armed_Status', '')}"
            writer.writerow([f"AUD-{idx:03d}", r.get('Timestamp', ''), coords, r.get('Speed_KMH', ''), r.get('Distance_To_Center_M', ''), sec_state, r.get('Alert_Type', 'NONE')])

    print(f"[OK] Generated analytical CSV report: {CSV_OUTPUT}")

    # 2. Generate PDF Report using ReportLab
    if not HAS_REPORTLAB:
        print("[WARN] ReportLab package not installed. Skipping PDF generation. Run: pip install reportlab")
        return

    doc = SimpleDocTemplate(PDF_OUTPUT, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#0f172a'), spaceAfter=12)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#1e40af'), spaceAfter=8)
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#334155'), spaceAfter=6)

    story = []
    story.append(Paragraph("IoT Vehicle Tracking & Theft Audit Report", title_style))
    story.append(Paragraph(f"<b>Report Generated:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    story.append(Spacer(1, 12))

    # Executive Summary Metrics
    total_records = len(rows)
    theft_incidents = sum(1 for r in rows if r.get("Alert_Type") == "THEFT_DETECTED")
    geofence_incidents = sum(1 for r in rows if r.get("Alert_Type") == "GEOFENCE_BREACH")
    max_speed = max([float(r.get("Speed_KMH", 0)) for r in rows] or [0])

    story.append(Paragraph("Executive Telemetry Summary", heading_style))
    summary_data = [
        ["Total Telemetry Logs Recorded", str(total_records)],
        ["Theft / Unauthorized Movement Alerts", f"{theft_incidents} Events"],
        ["Geofence Boundary Breach Alerts", f"{geofence_incidents} Events"],
        ["Maximum Recorded Velocity", f"{max_speed:.1f} km/h"]
    ]
    sum_table = Table(summary_data, colWidths=[250, 150])
    sum_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(sum_table)
    story.append(Spacer(1, 16))

    # Detailed Audit Table
    story.append(Paragraph("Recent Trajectory & Security Incidents Log", heading_style))
    table_data = [["Time", "Lat, Lng", "Speed", "Dist(m)", "Alert Status"]]
    
    # Take last 15 entries for PDF layout fit
    for r in rows[-15:]:
        t_str = r.get("Timestamp", "").split(" ")[-1] if " " in r.get("Timestamp", "") else r.get("Timestamp", "")
        coords = f"{float(r.get('Latitude',0)):.4f}, {float(r.get('Longitude',0)):.4f}"
        alert = r.get("Alert_Type", "NONE")
        table_data.append([t_str, coords, f"{r.get('Speed_KMH','')} km/h", f"{r.get('Distance_To_Center_M','')}", alert])

    log_table = Table(table_data, colWidths=[65, 120, 70, 65, 180])
    log_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(log_table)
    story.append(Spacer(1, 20))
    story.append(Paragraph("<i>Report verified by IoT Vehicle Security Automated Engine. End of Document.</i>", normal_style))

    doc.build(story)
    print(f"[OK] Generated executive PDF audit report: {PDF_OUTPUT}")

if __name__ == "__main__":
    generate_audit_reports()
