"""Integrated data-structure pipeline used by the Flask service."""
from hash_index import HashTable
from avl import AVLTree
from graph import StationGraph
from rank import top_k_polluted, AlertQueue
from database import get_connection

def station_hash_index():
    table = HashTable()
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM stations").fetchall()
        for r in rows:
            table.put(r["station_id"], dict(r))
    return table

def latest_readings():
    with get_connection() as conn:
        rows = conn.execute("""
        SELECT s.station_id, s.city, r.timestamp, r.aqi
        FROM stations s JOIN readings r ON r.station_id=s.station_id
        WHERE r.timestamp = (
            SELECT MAX(r2.timestamp) FROM readings r2
            WHERE r2.station_id=s.station_id
        )
        """).fetchall()
    return [dict(r) for r in rows]

def build_avl(station_id):
    tree = AVLTree()
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT timestamp, aqi FROM readings
            WHERE station_id=? ORDER BY timestamp
        """, (station_id,)).fetchall()
    for r in rows:
        tree.insert(r["timestamp"], r["aqi"])
    return tree

def build_graph():
    # The report specifies a weighted station graph. Edge data should be
    # replaced by the project's actual station distances.
    g = StationGraph()
    with get_connection() as conn:
        stations = conn.execute("SELECT station_id FROM stations").fetchall()
    for s in stations:
        g.add_station(s["station_id"])
    # Connect stations in input order as a minimal working graph if explicit
    # distance edges are not supplied in a separate file.
    ids = [s["station_id"] for s in stations]
    for a, b in zip(ids, ids[1:]):
        g.add_edge(a, b, 1.0)
    return g

def inverse_distance_weighted(neighbours, latest_by_station):
    """Estimate a missing AQI from nearest stations using IDW."""
    num = den = 0.0
    for sid, distance in neighbours:
        aqi = latest_by_station.get(sid)
        if aqi is None:
            continue
        w = 1.0 / max(distance, 1e-9)
        num += w * aqi
        den += w
    return num / den if den else None

def ranking(k=5):
    data = latest_readings()
    return top_k_polluted([(r["city"], r["aqi"]) for r in data], k)

def alert_queue(limit=200):
    q = AlertQueue(limit)
    for r in latest_readings():
        q.raise_alert(r["city"], r["aqi"])
    return list(q.process_alerts())
