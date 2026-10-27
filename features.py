"""Deque-based time-series feature construction."""
from collections import deque
from datetime import datetime

def build_features(rows):
    """Chronological rows for one station.

    Uses t-1, t-24, rolling mean and weather/calendar features.
    Target is current AQI; rows must be chronological.
    """
    rows = sorted(rows, key=lambda r: r["timestamp"])
    history = deque(maxlen=24)
    output = []

    for r in rows:
        if len(history) >= 24 and r["aqi"] is not None:
            vals = [x["aqi"] for x in history if x["aqi"] is not None]
            if len(vals) >= 24:
                prev = history[-1]["aqi"]
                lag24 = history[0]["aqi"]
                rolling = sum(x["aqi"] for x in list(history)[-6:] if x["aqi"] is not None) / len([x for x in list(history)[-6:] if x["aqi"] is not None])
                dt = datetime.fromisoformat(r["timestamp"])
                output.append({
                    "timestamp": r["timestamp"],
                    "x": [
                        float(prev), float(lag24), float(rolling),
                        float(r["pm25"] or 0), float(r["pm10"] or 0),
                        float(r["temperature"] or 0), float(r["humidity"] or 0),
                        float(dt.hour), float(dt.weekday())
                    ],
                    "y": float(r["aqi"])
                })
        history.append(r)
    return output
