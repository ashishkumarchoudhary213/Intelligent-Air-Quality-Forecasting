"""SQLite persistence for stations, readings and forecasts."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("air_quality.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS stations(
            station_id TEXT PRIMARY KEY,
            city TEXT NOT NULL,
            latitude REAL,
            longitude REAL
        );
        CREATE TABLE IF NOT EXISTS readings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            pm25 REAL,
            pm10 REAL,
            temperature REAL,
            humidity REAL,
            aqi REAL,
            UNIQUE(station_id,timestamp),
            FOREIGN KEY(station_id) REFERENCES stations(station_id)
        );
        CREATE TABLE IF NOT EXISTS forecasts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id TEXT NOT NULL,
            forecast_time TEXT NOT NULL,
            predicted_aqi REAL NOT NULL,
            model TEXT NOT NULL
        );
        """)
