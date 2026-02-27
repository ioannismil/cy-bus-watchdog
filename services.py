"""
services.py - GTFS-RT data fetching and stop loading.
"""

import csv
import json
import os
import time
import threading
import urllib.request

from google.transit import gtfs_realtime_pb2

from config import GTFS_RT_URL, STOPS_FILE, CACHE_TTL, BASE_DIR

_cache_lock = threading.Lock()
_cache = {"data": None, "timestamp": 0}
_stops = None
_gtfs_stops = None


def fetch_vehicles():
    """Fetch vehicle positions and trip updates from the GTFS-RT feed.
    Results are cached for CACHE_TTL seconds (thread-safe)."""
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
                    "speed": round(v.position.speed * 3.6, 1),  # m/s -> km/h
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
    """Load bus stops from CSV. Cached after first load."""
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
        print(f"Warning: {STOPS_FILE} not found. Stops endpoint will return empty.")

    _stops = stops
    return stops


def load_gtfs_stops():
    """Load GTFS static stops (stop_id-keyed). Cached after first load."""
    global _gtfs_stops
    if _gtfs_stops is not None:
        return _gtfs_stops

    path = os.path.join(BASE_DIR, "data", "gtfs_stops.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            _gtfs_stops = json.load(f)
    except FileNotFoundError:
        print(f"Warning: {path} not found. GTFS stops endpoint will return empty.")
        _gtfs_stops = []

    return _gtfs_stops
