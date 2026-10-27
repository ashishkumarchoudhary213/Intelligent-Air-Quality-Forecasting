import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from aqi import pm25_subindex
from window import RollingMean
from avl import AVLTree
from hash_index import HashTable
from graph import StationGraph
from rank import top_k_polluted, AlertQueue

def test_aqi():
    assert pm25_subindex(30) == 50

def test_deque():
    w=RollingMean(3)
    assert w.update(1)==1
    assert w.update(2)==1.5
    assert w.update(3)==2
    assert w.update(4)==3

def test_avl():
    t=AVLTree()
    for x in [5,3,8,2,4,7,9]:
        t.insert(x,x)
    assert [k for k,v in t.range_query(3,8)] == [3,4,5,7,8]

def test_hash():
    h=HashTable()
    h.put("ST001", {"city":"Noida"})
    assert h.get("ST001")["city"]=="Noida"

def test_dijkstra():
    g=StationGraph()
    g.add_edge("A","B",2)
    g.add_edge("B","C",3)
    assert g.nearest_stations("A",1)[0] == ("B",2)

def test_heap_queue():
    assert top_k_polluted([("A",100),("B",300),("C",200)],2)[0][0]=="B"
    q=AlertQueue(200)
    q.raise_alert("Delhi",250)
    assert list(q.process_alerts())[0] == ("Delhi",250.0)
