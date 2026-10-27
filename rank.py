"""Heap top-k ranking and FIFO alert queue."""
import heapq
from collections import deque

def top_k_polluted(readings, k):
    """readings = [(station, aqi)]; returns largest k AQI values."""
    return heapq.nlargest(k, readings, key=lambda r: r[1])

class AlertQueue:
    def __init__(self, limit=200):
        self.limit = limit
        self.queue = deque()

    def raise_alert(self, city, aqi):
        if float(aqi) > self.limit:
            self.queue.append((city, float(aqi)))

    def process_alerts(self):
        while self.queue:
            yield self.queue.popleft()
