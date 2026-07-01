"""
🌐 Geofence Engine - Spherical Haversine Mathematical Model
===========================================================
Calculates great-circle distance between two GPS coordinates (Latitude, Longitude)
on Earth using exact trigonometric formulas. Used by both the Python simulator
and replicated in C++ for the ESP32 firmware.
"""

import math

class GeofenceEngine:
    def __init__(self, center_lat=28.6139, center_lng=77.2090, radius_meters=500.0):
        """
        Initialize Geofence Engine with safe zone center coordinates and radius.
        Default center: Connaught Place, New Delhi (28.6139, 77.2090)
        Default safe radius: 500 meters.
        """
        self.center_lat = center_lat
        self.center_lng = center_lng
        self.radius_meters = radius_meters

    def calculate_haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate the great-circle distance between two points on Earth in meters.
        
        Formula:
          a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
          c = 2 ⋅ atan2( √a, √(1−a) )
          d = R ⋅ c
        where φ is latitude, λ is longitude, R is Earth's radius (6371 km).
        """
        R = 6371000.0  # Earth radius in meters

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0)**2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
        
        # Guard against domain error due to floating point precision
        a = min(1.0, max(0.0, a))
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

        distance = R * c
        return round(distance, 2)

    def check_geofence(self, current_lat, current_lng):
        """
        Evaluates whether the given coordinate is within the designated geofence radius.
        
        Returns:
            dict: {
                "is_inside": bool,
                "distance_meters": float,
                "radius_meters": float,
                "status": "INSIDE_GEOFENCE" or "BREACHED_GEOFENCE"
            }
        """
        dist = self.calculate_haversine_distance(self.center_lat, self.center_lng, current_lat, current_lng)
        is_inside = dist <= self.radius_meters
        
        return {
            "is_inside": is_inside,
            "distance_meters": dist,
            "radius_meters": self.radius_meters,
            "status": "INSIDE_GEOFENCE" if is_inside else "BREACHED_GEOFENCE"
        }

    def set_safe_center(self, lat, lng, radius_meters=None):
        """Updates the safe zone origin point."""
        self.center_lat = lat
        self.center_lng = lng
        if radius_meters is not None:
            self.radius_meters = radius_meters
