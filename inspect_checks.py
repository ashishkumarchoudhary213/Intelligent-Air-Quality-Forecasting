
from avl import AVLTree
from hash_index import HashTable
from graph import StationGraph
from rank import top_k_polluted,AlertQueue
t=AVLTree()
for i in range(1024): t.insert(f"{i:04d}",i)
h=HashTable(); h.put("ST001",{"city":"Delhi"})
g=StationGraph(); g.add_edge("A","B",2); g.add_edge("B","C",3)
q=AlertQueue(200); q.raise_alert("Delhi",250)
checks=[
 [k for k,v in t.range_query("0002","0008")]==list(range(2,9)),
 h.get("ST001")["city"]=="Delhi",
 g.nearest_stations("A",1)==[("B",2.0)],
 top_k_polluted([("A",100),("B",300),("C",200)],2)[0][0]=="B",
 list(q.process_alerts())==[("Delhi",250.0)],
 t.root.h<=12]
print(t.root.h)
print(checks)
