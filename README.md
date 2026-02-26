# Cyprus Real-Time Bus Tracker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE) [![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/) [![Flask](https://img.shields.io/badge/Flask-3.1-000000)](https://flask.palletsprojects.com/)

<p align="center">
  <img src="static/images/logo.png" alt="Cyprus Bus Tracker Logo" width="200">
</p>

A real-time bus tracker for Cyprus, consuming GTFS-Realtime data and
displaying live vehicle positions on an interactive map.

## Project Structure

```
app.py              Flask routes (entry point)
config.py           Configuration (env vars with defaults)
services.py         GTFS-RT fetching, stop loading, caching
static/
  bus_tracker.html  Single-page app (Leaflet map)
data/
  stops.csv         ~7 000 bus stops (semicolon-delimited)
```

---

## Getting Started

### Local development

```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
# .venv\Scripts\activate       # Windows
pip install -r requirements.txt
python app.py
```

Open http://localhost:8080 in your browser.

### Docker

```bash
docker build -t cy-bus-watchdog .
docker run -p 8080:8080 cy-bus-watchdog
```

### Production (Gunicorn)

```bash
gunicorn app:app --bind 0.0.0.0:8080 --workers 2
```

---

## Configuration

All settings can be overridden via environment variables (see `.env.example`):

| Variable      | Default                                          | Description                      |
| ------------- | ------------------------------------------------ | -------------------------------- |
| `PORT`        | `8080`                                           | Server port                      |
| `GTFS_RT_URL` | `http://20.19.98.194:8328/Api/api/gtfs-realtime` | GTFS-RT protobuf feed URL        |
| `STOPS_FILE`  | `data/stops.csv`                                 | Path to stops CSV file           |
| `CACHE_TTL`   | `10`                                             | Vehicle cache duration (seconds) |

---

## Dependencies

| Package                | Version | Purpose                   |
| ---------------------- | ------- | ------------------------- |
| Flask                  | 3.1.0   | Web framework             |
| gunicorn               | 23.0.0  | Production WSGI server    |
| gtfs-realtime-bindings | 2.0.0   | GTFS-RT protobuf bindings |
| protobuf               | 4.25+   | Protocol Buffers runtime  |

Install with `pip install -r requirements.txt`.

---

## License

MIT -- see [LICENSE](./LICENSE).
