"""Explicit hash table with separate chaining and resizing.

Used for station_id -> station metadata/latest reading lookup.
"""

class HashTable:
    def __init__(self, capacity=8, max_load=0.75):
        self.capacity = max(2, capacity)
        self.max_load = max_load
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0

    def _index(self, key):
        return hash(key) % self.capacity

    def _resize(self):
        old = self.buckets
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        for bucket in old:
            for key, value in bucket:
                self.buckets[self._index(key)].append((key, value))

    def put(self, key, value):
        idx = self._index(key)
        bucket = self.buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self.size += 1
        if self.size / self.capacity > self.max_load:
            self._resize()

    def get(self, key, default=None):
        for k, value in self.buckets[self._index(key)]:
            if k == key:
                return value
        return default

    def __contains__(self, key):
        return self.get(key, object()) is not None

    def __len__(self):
        return self.size
