from pytest import fixture

from plasma.node import Node


Node.min_size_default = 10

@fixture
def root():
    root = Node('root', 0, 0, 120, 50)
    return root

@fixture
def tiny_grid(root):
    a, b, c = Nodes('a b c')
    root.add_child(a)
    root.add_child(b)
    b.split_with(c)
    return a, b, c

@fixture
def small_grid(root):
    a, b, c, d = Nodes('a b c d')
    root.add_child(a)
    root.add_child(b)
    b.split_with(c)
    c.split_with(d)
    return a, b, c, d

@fixture
def grid(root):
    a, b, c, d, e = Nodes('a b c d e')
    root.add_child(a)
    root.add_child(b)
    b.split_with(c)
    c.split_with(d)
    c.parent.add_child(e)
    return a, b, c, d, e

@fixture
def complex_grid(root):
    a, b, c, d, e, f, g = Nodes('a b c d e f g')
    root.add_child(a)
    root.add_child(b)
    b.split_with(c)
    c.split_with(d)
    c.parent.add_child(e)
    c.split_with(f)
    f.split_with(g)
    return a, b, c, d, e, f, g

def Nodes(string):
    for x in string.split():
        yield Node(x)
