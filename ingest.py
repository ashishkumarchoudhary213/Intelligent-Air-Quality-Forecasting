"""CSV ingestion and cleaning.

Expected columns:
station_id, city, timestamp, pm25, pm10, temperature, humidity
latitude/longitude are optional.
"""

import csv
from datetime import datetime
from database import get_connection
from aqi import pm25_subindex

NUMERIC = ("pm25", "pm10", "temperature", "humidity")

def _num(v):
    if v in (None, "", "NA", "NaN", "nan"):
        return None
    return float(v)

def clean_rows(path):
    seen = set()
    rows = []
    imputed = 0
    with open(path, newline="", encoding="utf-8-sig") as f:
        for raw in csv.DictReader(f):
            station_id = raw["station_id"].strip()
            city = raw["city"].strip()
            ts = datetime.fromisoformat(raw["timestamp"]).isoformat()
            vals = {k: _num(raw.get(k)) for k in NUMERIC}

            # Cap physically implausible pollutant values for the prototype.
            if vals["pm25"] is not None:
                vals["pm25"] = max(0, min(vals["pm25"], 500))
            if vals["pm10"] is not None:
                vals["pm10"] = max(0, min(vals["pm10"], 600))

            key = (station_id, ts)
            if key in seen:
                continue
            seen.add(key)

            aqi = pm25_subindex(vals["pm25"]) if vals["pm25"] is not None else None
            rows.append({
                "station_id": station_id, "city": city, "timestamp": ts,
                **vals, "aqi": aqi,
                "latitude": _num(raw.get("latitude")),
                "longitude": _num(raw.get("longitude")),
            })

    # Short missing-value interpolation within each station.
    rows.sort(key=lambda r: (r["station_id"], r["timestamp"]))
    for station in sorted({r["station_id"] for r in rows}):
        sr = [r for r in rows if r["station_id"] == station]
        for field in NUMERIC:
            for i, r in enumerate(sr):
                if r[field] is None and 0 < i < len(sr)-1:
                    prev_v, next_v = sr[i-1][field], sr[i+1][field]
                    if prev_v is not None and next_v is not None:
                        r[field] = (prev_v + next_v) / 2
                        imputed += 1
        for r in sr:
            if r["pm25"] is not None:
                r["aqi"] = pm25_subindex(r["pm25"])
    return rows, imputed

def ingest_csv(path):
    rows, imputed = clean_rows(path)
    with get_connection() as conn:
        for r in rows:
            conn.execute("""
                INSERT INTO stations(station_id,city,latitude,longitude)
                VALUES(?,?,?,?)
                ON CONFLICT(station_id) DO UPDATE SET
                    city=excluded.city,
                    latitude=excluded.latitude,
                    longitude=excluded.longitude
            """, (r["station_id"], r["city"], r["latitude"], r["longitude"]))

            conn.execute("""
                INSERT INTO readings(
                    station_id,timestamp,pm25,pm10,temperature,humidity,aqi
                ) VALUES(?,?,?,?,?,?,?)
                ON CONFLICT(station_id,timestamp) DO UPDATE SET
                    pm25=excluded.pm25, pm10=excluded.pm10,
                    temperature=excluded.temperature,
                    humidity=excluded.humidity, aqi=excluded.aqi
            """, (r["station_id"], r["timestamp"], r["pm25"], r["pm10"],
                  r["temperature"], r["humidity"], r["aqi"]))
    return len(rows), imputed
