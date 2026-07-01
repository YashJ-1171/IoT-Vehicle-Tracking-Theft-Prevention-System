/**
 * 🖥️ Frontend Command Center Logic - Leaflet & Chart.js Integration
 * Polls Flask REST endpoints in real-time to update maps, UI badges, and analytics.
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Initialize Leaflet Map
    const initialLat = 28.6139;
    const initialLng = 77.2090;
    const map = L.map("map").setView([initialLat, initialLng], 15);

    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; OpenStreetMap & CartoDB',
        maxZoom: 19
    }).addTo(map);

    // Vehicle Marker & Safe Geofence Overlay Circle
    const vehicleIcon = L.divIcon({
        className: 'vehicle-marker',
        html: '<div style="font-size:28px;">🚗</div>',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });

    let vehicleMarker = L.marker([initialLat, initialLng], { icon: vehicleIcon }).addTo(map);
    let geofenceCircle = L.circle([initialLat, initialLng], {
        color: '#38bdf8',
        fillColor: '#38bdf8',
        fillOpacity: 0.12,
        radius: 500
    }).addTo(map);

    // 2. Initialize Chart.js
    const ctx = document.getElementById("telemetryChart").getContext("2d");
    const telemetryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Speed (km/h)',
                    data: [],
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'Geofence Distance (m)',
                    data: [],
                    borderColor: '#f59e0b',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            },
            plugins: { legend: { labels: { color: '#f0f4f8' } } }
        }
    });

    // 3. Real-time Telemetry Polling Loop
    async function updateDashboard() {
        try {
            const resp = await fetch("/api/telemetry");
            const data = await resp.json();

            // Update Map Marker
            if (data.latitude && data.longitude) {
                const newLatLng = [data.latitude, data.longitude];
                vehicleMarker.setLatLng(newLatLng);
                map.panTo(newLatLng);
            }

            // Update Metrics Cards
            document.getElementById("coords-val").textContent = `${data.latitude?.toFixed(6)}, ${data.longitude?.toFixed(6)}`;
            document.getElementById("speed-val").innerHTML = `${data.speed_kmh?.toFixed(1)} <small>km/h</small>`;
            document.getElementById("dist-val").innerHTML = `${data.distance_meters?.toFixed(1)} <small>m</small>`;
            document.getElementById("google-maps-link").href = data.maps_url || "#";

            // Update Status Banner
            const banner = document.getElementById("system-status-banner");
            const statusText = document.getElementById("status-text");
            statusText.textContent = data.status || "NORMAL";

            if (data.alert_type === "THEFT_DETECTED") {
                banner.style.background = "rgba(239, 68, 68, 0.25)";
                banner.style.borderColor = "#ef4444";
                banner.querySelector(".status-indicator").style.background = "#ef4444";
            } else if (data.alert_type === "GEOFENCE_BREACH") {
                banner.style.background = "rgba(245, 158, 11, 0.25)";
                banner.style.borderColor = "#f59e0b";
                banner.querySelector(".status-indicator").style.background = "#f59e0b";
            } else {
                banner.style.background = "rgba(16, 185, 129, 0.15)";
                banner.style.borderColor = "#10b981";
                banner.querySelector(".status-indicator").style.background = "#10b981";
            }

            // Update Actuator Badges
            document.getElementById("ind-ignition").querySelector(".actuator-state").textContent = data.ignition_on ? "ON" : "OFF";
            document.getElementById("ind-armed").querySelector(".actuator-state").textContent = data.is_armed ? "ARMED" : "DISARMED";
            
            const buzzerBadge = document.getElementById("ind-buzzer").querySelector(".actuator-state");
            buzzerBadge.textContent = data.buzzer_alarm ? "🚨 ALARMING" : "SILENT";
            buzzerBadge.className = data.buzzer_alarm ? "actuator-state state-danger" : "actuator-state state-active";

            const relayBadge = document.getElementById("ind-relay").querySelector(".actuator-state");
            relayBadge.textContent = data.relay_cut ? "⚡ CUT-OFF" : "NORMAL";
            relayBadge.className = data.relay_cut ? "actuator-state state-danger" : "actuator-state state-active";

            // Update Chart
            const timeLabel = new Date().toLocaleTimeString();
            if (telemetryChart.data.labels.length > 15) {
                telemetryChart.data.labels.shift();
                telemetryChart.data.datasets[0].data.shift();
                telemetryChart.data.datasets[1].data.shift();
            }
            telemetryChart.data.labels.push(timeLabel);
            telemetryChart.data.datasets[0].data.push(data.speed_kmh);
            telemetryChart.data.datasets[1].data.push(data.distance_meters);
            telemetryChart.update('none');

        } catch (err) {
            console.warn("Waiting for dashboard API response...", err);
        }
    }

    setInterval(updateDashboard, 1500);
});

// Trigger simulation scenario button action
async function triggerSimulation(scenario) {
    try {
        await fetch("/api/control", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: scenario })
        });
        console.log(`Triggered simulation: ${scenario}`);
    } catch (err) {
        console.error("Error triggering simulation:", err);
    }
}
