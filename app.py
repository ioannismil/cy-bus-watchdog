"""
Cyprus Real-Time Bus Tracker - Production Server (Flask)

Local:    python app.py
Production: gunicorn app:app
"""

import json
import os
import time
import csv
import urllib.request
import threading

from flask import Flask, jsonify, send_from_directory
from google.transit import gtfs_realtime_pb2

app = Flask(__name__, static_folder=".", static_url_path="")

GTFS_RT_URL = "http://20.19.98.194:8328/Api/api/gtfs-realtime"
STOPS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stops.csv")
CACHE_TTL = 10

_cache_lock = threading.Lock()
_cache = {"data": None, "timestamp": 0}
_stops = None


def fetch_vehicles():
    now = time.time()
    with _cache_lock:
        if _cache["data"] and now - _cache["timestamp"] < CACHE_TTL:
            return _cache["data"]

    try:
        req = urllib.request.Request(GTFS_RT_URL)
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read()

        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(raw)

        vehicles = []
        trip_updates = []

        for entity in feed.entity:
            if entity.HasField("vehicle"):
                v = entity.vehicle
                vehicles.append({
                    "id": v.vehicle.id or v.vehicle.label,
                    "label": v.vehicle.label,
                    "lat": round(v.position.latitude, 6),
                    "lon": round(v.position.longitude, 6),
                    "bearing": v.position.bearing,
                    "speed": round(v.position.speed * 3.6, 1),
                    "trip_id": v.trip.trip_id,
                    "route_id": v.trip.route_id,
                    "timestamp": v.timestamp,
                })
            if entity.HasField("trip_update"):
                tu = entity.trip_update
                trip_updates.append({
                    "trip_id": tu.trip.trip_id,
                    "route_id": tu.trip.route_id,
                    "start_time": tu.trip.start_time,
                    "vehicle": tu.vehicle.label if tu.HasField("vehicle") else None,
                    "stops": [
                        {
                            "stop_id": s.stop_id,
                            "arrival": s.arrival.time if s.HasField("arrival") else None,
                            "departure": s.departure.time if s.HasField("departure") else None,
                        }
                        for s in tu.stop_time_update
                    ],
                })

        result = {
            "timestamp": feed.header.timestamp,
            "vehicle_count": len(vehicles),
            "trip_update_count": len(trip_updates),
            "vehicles": vehicles,
            "trip_updates": trip_updates,
        }

        with _cache_lock:
            _cache["data"] = result
            _cache["timestamp"] = now

        return result

    except Exception as e:
        return {"error": str(e), "vehicles": [], "trip_updates": [], "vehicle_count": 0}


def load_stops():
    global _stops
    if _stops is not None:
        return _stops

    stops = []
    try:
        with open(STOPS_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                try:
                    stops.append({
                        "code": row["code"],
                        "name_el": row.get("description[el]", ""),
                        "name_en": row.get("description[en]", row.get("description", "")),
                        "lat": float(row["lat"].replace(",", ".")),
                        "lon": float(row["lon"].replace(",", ".")),
                    })
                except (ValueError, KeyError):
                    continue
    except FileNotFoundError:
        pass

    _stops = stops
    return stops


@app.route("/")
def index():
    return send_from_directory(".", "bus_tracker.html")


@app.route("/api/vehicles")
def api_vehicles():
    return jsonify(fetch_vehicles())


@app.route("/api/stops")
def api_stops():
    return jsonify(load_stops())


if __name__ == "__main__":
    stops = load_stops()
    print(f"Loaded {len(stops)} bus stops")

    result = fetch_vehicles()
    if "error" in result:
        print(f"Warning: GTFS-RT fetch failed: {result['error']}")
    else:
        print(f"Connected! {result['vehicle_count']} vehicles")

    port = int(os.environ.get("PORT", 8080))
    print(f"\n  Bus Tracker: http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
