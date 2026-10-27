"""AVL tree keyed by timestamp, with range query."""

class Node:
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.left = self.right = None
        self.h = 1

def h(n): return n.h if n else 0
def upd(n): n.h = 1 + max(h(n.left), h(n.right))
def bal(n): return h(n.left) - h(n.right)

def rot_right(y):
    x = y.left
    y.left, x.right = x.right, y
    upd(y); upd(x)
    return x

def rot_left(x):
    y = x.right
    x.right, y.left = y.left, x
    upd(x); upd(y)
    return y

def insert(n, key, val):
    if not n:
        return Node(key, val)
    if key < n.key:
        n.left = insert(n.left, key, val)
    elif key > n.key:
        n.right = insert(n.right, key, val)
    else:
        n.val = val
        return n

    upd(n)
    b = bal(n)

    if b > 1:
        if bal(n.left) < 0:
            n.left = rot_left(n.left)
        return rot_right(n)
    if b < -1:
        if bal(n.right) > 0:
            n.right = rot_right(n.right)
        return rot_left(n)
    return n

def range_query(n, lo, hi, out=None):
    """All (key, val) with lo <= key <= hi, in order."""
    if out is None:
        out = []
    if not n:
        return out
    if lo < n.key:
        range_query(n.left, lo, hi, out)
    if lo <= n.key <= hi:
        out.append((n.key, n.val))
    if n.key < hi:
        range_query(n.right, lo, hi, out)
    return out

class AVLTree:
    def __init__(self):
        self.root = None

    def insert(self, key, val):
        self.root = insert(self.root, key, val)

    def range_query(self, lo, hi):
        return range_query(self.root, lo, hi)
