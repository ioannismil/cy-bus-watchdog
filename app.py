"""
Cyprus Real-Time Bus Tracker - Flask Server

Local:      python app.py
Production: gunicorn app:app
"""

import os

from flask import Flask, jsonify, send_from_directory

from config import PORT
from services import fetch_vehicles, load_stops, load_gtfs_stops

app = Flask(__name__, static_folder="static", static_url_path="/static")


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "bus_tracker.html")


@app.route("/api/vehicles")
def api_vehicles():
    return jsonify(fetch_vehicles())


@app.route("/api/stops")
def api_stops():
    return jsonify(load_stops())


@app.route("/api/gtfs-stops")
def api_gtfs_stops():
    return jsonify(load_gtfs_stops())


if __name__ == "__main__":
    stops = load_stops()
    print(f"Loaded {len(stops)} bus stops")

    result = fetch_vehicles()
    if "error" in result:
        print(f"Warning: GTFS-RT fetch failed: {result['error']}")
    else:
        print(f"Connected! {result['vehicle_count']} vehicles")

    print(f"\n  Bus Tracker: http://localhost:{PORT}\n")
    app.run(host="0.0.0.0", port=PORT, debug=False)
