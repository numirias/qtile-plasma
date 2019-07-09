from pathlib import Path
import sys

from pytest import fixture

from plasma.node import Node

# We borrow Qtile's testing framework. That's not elegant but the best option.
sys.path.insert(0, str(Path(__file__).parents[1] / 'lib'))  # noqa: E402
from qtile.test.conftest import pytest_addoption



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
    b.flip_with(c)
    return a, b, c

@fixture
def small_grid(root):
    a, b, c, d = Nodes('a b c d')
    root.add_child(a)
    root.add_child(b)
    b.flip_with(c)
    c.flip_with(d)
    return a, b, c, d

@fixture
def grid(root):
    a, b, c, d, e = Nodes('a b c d e')
    root.add_child(a)
    root.add_child(b)
    b.flip_with(c)
    c.flip_with(d)
    c.parent.add_child(e)
    return a, b, c, d, e

@fixture
def complex_grid(root):
    a, b, c, d, e, f, g = Nodes('a b c d e f g')
    root.add_child(a)
    root.add_child(b)
    b.flip_with(c)
    c.flip_with(d)
    c.parent.add_child(e)
    c.flip_with(f)
    f.flip_with(g)
    return a, b, c, d, e, f, g

def Nodes(string):
    for x in string.split():
        yield Node(x)
