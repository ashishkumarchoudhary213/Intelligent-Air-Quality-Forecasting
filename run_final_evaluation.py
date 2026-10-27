import json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from database import init_db,get_connection
from ingest import ingest_csv
from model import evaluate_station
from avl import AVLTree
from hash_index import HashTable
from graph import StationGraph
from rank import top_k_polluted, AlertQueue

db=Path(__file__).with_name("air_quality.db")
if db.exists(): db.unlink()
init_db()
n,imp=ingest_csv(str(Path(__file__).parent/"data"/"benchmark_air_quality.csv"))
with get_connection() as conn:
    ids=[r["station_id"] for r in conn.execute("SELECT station_id FROM stations")]

per={}
for sid in ids:
    with get_connection() as conn:
        rows=[dict(r) for r in conn.execute("SELECT * FROM readings WHERE station_id=? ORDER BY timestamp",(sid,)).fetchall()]
    per[sid]=evaluate_station(rows)

names=["Persistence","Linear Regression","Random Forest","Gradient Boosting"]
agg={name:{m:sum(per[s]["results"][name][m] for s in ids)/len(ids) for m in ["MAE","RMSE"]} for name in names}
best=min(agg,key=lambda x:agg[x]["MAE"])

t=AVLTree()
for i in range(1024): t.insert(f"{i:04d}",i)
h=HashTable(); h.put("ST001",{"city":"Delhi"})
g=StationGraph(); g.add_edge("A","B",2); g.add_edge("B","C",3)
q=AlertQueue(200); q.raise_alert("Delhi",250)
checks=[
 [k for k,v in t.range_query("0002","0008")]==[f"{i:04d}" for i in range(2,9)],
 h.get("ST001")["city"]=="Delhi",
 g.nearest_stations("A",1)==[("B",2.0)],
 top_k_polluted([("A",100),("B",300),("C",200)],2)[0][0]=="B",
 list(q.process_alerts())==[("Delhi",250.0)],
 t.root.h<=12]
out={"rows_loaded":n,"values_imputed":imp,"stations":len(ids),"hours_per_station":2160,
"aggregate":agg,"best_model":best,"avl_height_1024_sorted":t.root.h,
"dsa_unit_tests":f"{sum(checks)} of {len(checks)} passed"}
Path(__file__).with_name("evaluation_results.json").write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
