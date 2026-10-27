"""Flask API and dashboard for the Intelligent Air Quality Forecasting System."""
from flask import Flask, jsonify, request, render_template
from database import init_db, get_connection
from ingest import ingest_csv
from model import evaluate_station, predict_next
from pipeline import station_hash_index, build_avl, build_graph, ranking, alert_queue
from aqi import aqi_category

app = Flask(__name__)
init_db()

def station_rows():
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM stations ORDER BY city"
        ).fetchall()]

def readings(station_id, limit=10000):
    with get_connection() as conn:
        return [dict(r) for r in conn.execute("""
            SELECT * FROM readings
            WHERE station_id=?
            ORDER BY timestamp
            LIMIT ?
        """, (station_id, limit)).fetchall()]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/stations")
def api_stations():
    return jsonify(station_rows())

@app.route("/api/forecast/<station_id>")
def api_forecast(station_id):
    rows = readings(station_id)
    try:
        pred, model_name = predict_next(rows)
        return jsonify({
            "station_id": station_id,
            "forecast_24h": round(pred, 2),
            "category": aqi_category(pred),
            "model": model_name
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/train", methods=["POST"])
def api_train():
    station_id = (request.get_json(silent=True) or {}).get("station_id")
    if not station_id:
        return jsonify({"error": "station_id is required"}), 400
    try:
        result = evaluate_station(readings(station_id))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/history/<station_id>")
def api_history(station_id):
    return jsonify([
        {"timestamp": r["timestamp"], "aqi": r["aqi"]}
        for r in readings(station_id, 1000)
    ])

@app.route("/api/history-range/<station_id>")
def api_history_range(station_id):
    rows = readings(station_id)
    if not rows:
        return jsonify([])
    tree = build_avl(station_id)
    lo = request.args.get("from", rows[0]["timestamp"])
    hi = request.args.get("to", rows[-1]["timestamp"])
    return jsonify([{"timestamp": k, "aqi": v}
                    for k, v in tree.range_query(lo, hi)])

@app.route("/api/ranking")
def api_ranking():
    k = int(request.args.get("k", 5))
    return jsonify([
        {"city": city, "aqi": round(float(aqi), 2), "category": aqi_category(aqi)}
        for city, aqi in ranking(k)
    ])

@app.route("/api/alerts")
def api_alerts():
    return jsonify([
        {"city": city, "aqi": round(aqi, 2)}
        for city, aqi in alert_queue(200)
    ])

@app.route("/api/neighbours/<station_id>")
def api_neighbours(station_id):
    k = int(request.args.get("k", 3))
    result = build_graph().nearest_stations(station_id, k)
    return jsonify([{"station_id": s, "distance": round(d, 3)}
                    for s, d in result])

@app.route("/api/cluster/<station_id>")
def api_cluster(station_id):
    return jsonify(build_graph().bfs_cluster(station_id))

@app.route("/api/station-lookup/<station_id>")
def api_station_lookup(station_id):
    station = station_hash_index().get(station_id)
    if station is None:
        return jsonify({"error": "Station not found"}), 404
    return jsonify(station)

@app.route("/api/ingest", methods=["POST"])
def api_ingest():
    # Multipart field: file
    if "file" not in request.files:
        return jsonify({"error": "Upload a CSV in form field 'file'."}), 400
    f = request.files["file"]
    if not f.filename.lower().endswith(".csv"):
        return jsonify({"error": "CSV file required."}), 400
    temp = "uploaded_air_quality.csv"
    f.save(temp)
    try:
        count, imputed = ingest_csv(temp)
        return jsonify({"rows_loaded": count, "values_imputed": imputed})
    finally:
        import os
        if os.path.exists(temp):
            os.remove(temp)

if __name__ == "__main__":
    app.run(debug=True)
