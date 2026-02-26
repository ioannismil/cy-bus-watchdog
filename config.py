"""
config.py - All configuration in one place. Override via environment variables.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GTFS_RT_URL = os.environ.get(
    "GTFS_RT_URL",
    "http://20.19.98.194:8328/Api/api/gtfs-realtime",
)

STOPS_FILE = os.environ.get(
    "STOPS_FILE",
    os.path.join(BASE_DIR, "data", "stops.csv"),
)

CACHE_TTL = int(os.environ.get("CACHE_TTL", "10"))

PORT = int(os.environ.get("PORT", "8080"))
