"""Station graph, Dijkstra nearest-neighbour search and BFS clusters."""
import heapq
from collections import deque

class StationGraph:
    def __init__(self):
        self.adj = {}

    def add_station(self, station):
        self.adj.setdefault(station, [])

    def add_edge(self, u, v, km, bidirectional=True):
        self.add_station(u)
        self.add_station(v)
        self.adj[u].append((v, float(km)))
        if bidirectional:
            self.adj[v].append((u, float(km)))

    def nearest_stations(self, src, k):
        if src not in self.adj:
            return []
        dist = {src: 0.0}
        pq = [(0.0, src)]
        out = []
        while pq and len(out) < k:
            d, u = heapq.heappop(pq)
            if d > dist.get(u, float("inf")):
                continue
            if u != src:
                out.append((u, d))
            for v, w in self.adj.get(u, []):
                nd = d + w
                if nd < dist.get(v, float("inf")):
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))
        return out[:k]

    def bfs_cluster(self, start):
        if start not in self.adj:
            return []
        q = deque([start])
        seen = {start}
        out = []
        while q:
            u = q.popleft()
            out.append(u)
            for v, _ in self.adj.get(u, []):
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        return out
