# Cyprus Real-Time Bus Tracker

A minimal server and frontend for displaying live bus locations in Cyprus using the
GTFS-Realtime feed.

This repository contains:

- `app.py` – Flask-based API server (production target via `gunicorn`).
- `bus_tracker_server.py` – lightweight http.server implementation (alternate entrypoint).
- `bus_tracker.html` – single-page frontend consuming the API.
- `stops.csv` – static list of stops used by the app.

---

## Versions & dependencies

| Component | Version | Notes |
|-----------|---------|-------|
| Python    | 3.11+  | Development/test environment |
| Flask     | 2.2+   | Web framework used in `app.py` |
| gtfs-realtime-bindings | 0.0.5+ | Protobuf bindings for GTFS-RT |
| protobuf  | 4.x    | Required by the bindings |

(install with `pip install -r requirements.txt`)

---

## Getting started

### Local

```bash
python -m venv .venv          # create virtualenv
.\.venv\Scripts\activate     # Windows
pip install -r requirements.txt
python app.py                  # or `python bus_tracker_server.py`
```

Browse `http://localhost:8080` to view the tracker.

### Production

Use Gunicorn to run the Flask app (the `Dockerfile` is configured accordingly):

```bash
gunicorn app:app --bind 0.0.0.0:8080
```

---

## License

This project is licensed under the MIT License – see [LICENSE](./LICENSE).

---

![Live buses](./bus_tracker.html)
