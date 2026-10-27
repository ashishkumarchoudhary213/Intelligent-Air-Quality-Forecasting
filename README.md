# Intelligent Air Quality Forecasting System — Final Source Code

This implementation is aligned to the submitted NIET DSA PBL report.

## Report-aligned modules

1. `ingest.py` — data parsing, duplicate removal, short-gap interpolation, pollutant capping, SQLite storage.
2. `hash_index.py` — explicit hash table with separate chaining and resizing.
3. `features.py` / `window.py` — deque/sliding-window features including t-1, t-24 and rolling mean.
4. `model.py` — chronological split; Persistence baseline, Linear Regression, Random Forest and Gradient Boosting; MAE/RMSE.
5. `avl.py` — AVL timestamp index and range query.
6. `graph.py` — weighted graph, Dijkstra nearest stations and BFS clustering.
7. `rank.py` — heap top-k ranking and FIFO alert queue.
8. `app.py` — Flask forecast/history/ranking/alert/lookup/nearest-station APIs and dashboard.
9. `database.py` — SQLite stations, readings and forecasts schema.

## Run

```bash
python -m venv venv
```

macOS/Linux:
```bash
source venv/bin/activate
```

Windows:
```bash
venv\Scripts\activate
```

Install:
```bash
pip install -r requirements.txt
```

Run tests:
```bash
pytest -q
```

Run:
```bash
python app.py
```

Then open:
`http://127.0.0.1:5000`

## Data

The original report does not include its raw AQI dataset, so this project does NOT fabricate one and does NOT claim model accuracy numbers.

Use a real historical/open CSV with:
`station_id,city,timestamp,pm25,pm10,temperature,humidity`

Upload it to:
`POST /api/ingest`
with multipart form field `file`.

Then use:
`POST /api/train`
with JSON:
`{"station_id":"YOUR_STATION_ID"}`

The response contains actual Persistence/Linear Regression/Random Forest/Gradient Boosting MAE and RMSE from that dataset.

## Important report-integrity note

The report mentions station-to-station distances for its weighted graph. Because those actual edge distances are not present in the report, `pipeline.py` uses a minimal connected graph when no distance-edge file is supplied. Replace those edges with the project's actual station distances before claiming real geographic nearest-neighbour results.

Similarly, the report says final test results come from project runs. Those numeric results are not present in the supplied report, so this code does not invent them.


## Data-integrity note
The original report did not include its raw AQI dataset. This package includes a deterministic synthetic benchmark dataset generated for reproducibility (`data/benchmark_air_quality.csv`). The MAE/RMSE values in the revised report are actual outputs of the included code on that benchmark. They are not claimed CPCB/OpenAQ field measurements.
