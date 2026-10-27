from avl import AVLTree
t=AVLTree()
for i in range(1024): t.insert(f"{i:04d}",i)
print(t.range_query("0002","0008"))