# 🌐 Complete Deployment Guide

This guide covers deploying the **IoT Vehicle Tracking & Theft Prevention System Command Center** across local networks, cloud hosting platforms, and Docker containers.

---

## 1️⃣ Option A: Local Deployment (Instant Windows / LAN Host)

To run the dashboard locally and allow anyone on your home or campus WiFi network (like a evaluator testing on their smartphone) to view live tracking:

1. Open PowerShell / Command Prompt inside the project directory.
2. Start the production server using Python:
   ```powershell
   python main.py --mode dashboard
   ```
3. Find your computer's Local IP Address by running `ipconfig` (e.g., `192.168.1.100`).
4. On your mobile phone or laptop connected to the same WiFi, open:
   ```
   http://192.168.1.100:5000
   ```
   *Note: Update your ESP32 Arduino code (`vehicle_tracker_esp32.ino`) `SERVER_URL` variable to match this IP!*

---

## 2️⃣ Option B: Free Cloud Deployment (Render / Railway / Heroku)

To host your web dashboard publicly on the internet (100% Free) so recruiters can view your working project from anywhere:

### Using Render.com (Recommended Free Cloud Hosting)
1. Push your project repository to GitHub.
2. Go to [https://render.com](https://render.com) and create a Free Account.
3. Click **New +** $\rightarrow$ **Web Service**.
4. Connect your GitHub repository (`IoT-Vehicle-Tracking-Theft-Prevention-System`).
5. Configure the deployment settings:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
6. Click **Create Web Service**. Within 2 minutes, Render will provide a live public URL!

---

### Using Vercel (Serverless Python Deployment)
We have configured your project with `vercel.json` and `api/index.py` for instant zero-config Vercel serverless deployment!

**Option A: Via GitHub (Simplest)**
1. Push this repository to GitHub.
2. Go to [https://vercel.com](https://vercel.com) and click **Add New Project**.
3. Import your GitHub repo (`IoT-Vehicle-Tracking-Theft-Prevention-System`).
4. Keep all default settings (Framework Preset: **Other**) and click **Deploy**.
5. Vercel will automatically build the `@vercel/python` serverless endpoint and give you a live production URL!

**Option B: Via Vercel CLI (From Terminal)**
If you have Node.js installed, open terminal in this folder and run:
```powershell
npx vercel --prod
```
Follow the interactive prompts to log in and deploy immediately!

---

## 3️⃣ Option C: Containerized Docker Deployment

If you or your organization uses Docker:

```bash
# Build Docker Image
docker build -t iot-vehicle-tracker .

# Run Docker Container on port 5000
docker run -d -p 5000:5000 --name tracker-app iot-vehicle-tracker
```
Access the application at `http://localhost:5000`.
