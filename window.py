"""Deque-based sliding window for lag and rolling features."""
from collections import deque

class RollingMean:
    def __init__(self, k):
        if k <= 0:
            raise ValueError("k must be positive")
        self.k = k
        self.win = deque()
        self.total = 0.0

    def update(self, x):
        self.win.append(float(x))
        self.total += float(x)
        if len(self.win) > self.k:
            self.total -= self.win.popleft()
        return self.total / len(self.win)
