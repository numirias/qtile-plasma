from pytest import fixture, approx

from plasma.debug import draw, tree, info
from plasma.node import Node, VERTICAL, HORIZONTAL


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

def Nodes(string):
    for x in string.split():
        yield Node(x)

class TestPlasma:

    def test_single_node(self):
        n = Node(None, 0, 0, 120, 50)
        assert n.x == 0
        assert n.y == 0
        assert n.width == 120
        assert n.height == 50
        assert n.is_root is True
        assert n.is_leaf is True
        assert n.parent is None
        assert n.children == []
        assert n.orient == HORIZONTAL
        assert n.horizontal is True
        assert n.vertical is False
        assert (n.x, n.y) == n.pos

    def test_add_child(self, root):
        child = Node('a')
        root.add_child(child)
        assert root.children == [child]
        assert child.parent == root
        assert root.width == child.width == 120
        assert root.height == child.height == 50
        assert root.x == child.x == 0
        assert root.y == child.y == 0

    def test_add_children(self, root):
        a, b = Nodes('a b')
        root.add_child(a)
        root.add_child(b)
        assert root.width == 120
        assert a.width == b.width == 60
        assert root.height == 50
        assert a.height == b.height == 50
        assert a.pos == (0, 0)
        assert b.pos == (60, 0)
        c = Node('c')
        root.add_child(c)
        assert a.width == b.width == c.width == 40
        assert a.pos == (0, 0)
        assert b.pos == (40, 0)
        assert c.pos == (80, 0)
        root._default_orient = VERTICAL
        assert a.width == b.width == c.width == 120
        assert a.height == b.height == c.height == 50/3
        assert a.pos == (0, 0)
        assert b.pos == (0, 50/3)
        assert c.pos == (0, 50/3*2)

    def test_add_child_after(self, root, grid):
        a, b, c, d, e = grid
        f = Node('f')
        g = Node('g')
        h = Node('h')
        root.add_child_after(f, a)
        assert root.tree == [a, f, [b, [c, d, e]]]
        b.parent.add_child_after(g, b)
        assert root.tree == [a, f, [b, g, [c, d, e]]]
        d.parent.add_child_after(h, d)
        assert root.tree == [a, f, [b, g, [c, d, h, e]]]

    def test_add_child_after_with_sizes(self, root):
        a, b, c = Nodes('a b c')
        root.add_child(a)
        root.add_child(b)
        a.grow(10)
        b.grow(10)
        b.parent.add_child_after(c, b)
        assert a.size == b.size == c.size == 40

    def test_remove_child(self, root):
        a, b = Nodes('a b')
        root.add_child(a)
        root.add_child(b)
        root.remove_child(a)
        assert root.children == [b]

    def test_nested(self, root):
        a, b, c, d = Nodes('a b c d')
        root.add_child(a)
        root.add_child(b)
        b.split_with(c)
        assert a.width == 60
        assert b.width == 60
        assert c.width == 60
        assert a.height == 50
        assert b.height == 25
        assert c.height == 25
        b.split_with(d)
        assert b.width == 30
        assert d.width == 30

    def test_leaves(self, root, grid):
        a, b, c, d, e = grid
        assert root.first_leaf is a
        assert root.last_leaf is e
        assert b.parent.first_leaf is b
        assert b.parent.last_leaf is e

    def test_directions(self, root, grid):
        a, b, c, d, e = grid
        assert a.up is None
        assert a.right is b
        assert a.down is None
        assert a.left is None

        assert b.up is None
        assert b.right is None
        assert b.down is c
        assert b.left is a

        assert c.up is b
        assert c.right is d
        assert c.down is None
        assert c.left is a

        assert d.up is b
        assert d.right is e
        assert d.down is None
        assert d.left is c

        assert e.up is b
        assert e.right is None
        assert e.down is None
        assert e.left is d

    def test_prev_next(self, grid):
        a, b, c, d, e = grid
        assert a.next == b
        assert b.next == c
        assert c.next == d
        assert d.next == e
        assert e.next == a
        assert a.prev == e
        assert e.prev == d
        assert d.prev == c
        assert c.prev == b
        assert b.prev == a

    def test_siblings(self, root, grid):
        a, b, c, d, e = grid
        assert d.siblings == [c, e]
        assert b.siblings == [c.parent]

    def test_simple_moving(self, grid):
        a, b, c, d, e = grid
        assert c.parent.children == [c, d, e]
        c.move_right()
        assert c.parent.children == [d, c, e]
        c.move_right()
        assert c.parent.children == [d, e, c]
        c.move_right()
        assert c.parent.children == [d, e, c]
        c.move_left()
        assert c.parent.children == [d, c, e]
        c.move_left()
        assert c.parent.children == [c, d, e]
        c.move_left()
        assert c.parent.children == [c, d, e]

    def test_advanced_moving(self, root, grid):
        a, b, c, d, e = grid
        c.move_up()
        assert b.parent.tree == [b, c, [d, e]]
        a.move_up()
        assert b.parent.tree == [b, c, [d, e]]

    def test_advanced_moving2(self, root, grid):
        a, b, c, d, e = grid
        c.move_down()
        assert b.parent.tree == [b, [d, e], c]
        e.move_down()
        assert b.parent.tree == [b, d, e, c]
        e.move_left()
        assert root.tree == [a, e, [b, d, c]]
        d.move_right()
        assert root.tree == [a, e, [b, c], d]
        a.move_left()
        assert root.tree == [a, e, [b, c], d]
        d.move_right()
        assert root.tree == [a, e, [b, c], d]

    def test_advanced_moving3(self, root, grid):
        # TODO c should be able to move left
        pass

    def test_integrate(self, root, grid):
        a, b, c, d, e = grid
        c.integrate(HORIZONTAL, -1)
        assert b.parent.tree == [b, [c, d, e]]
        c.integrate(VERTICAL, 1)
        assert b.parent.tree == [b, [c, d, e]]
        c.integrate(VERTICAL, -1)
        assert b.parent.tree == [b, [c, d, e]]
        c.integrate(HORIZONTAL, 1)
        assert b.parent.tree == [b, [[d, c], e]]
        f = Node('f')
        e.parent.add_child(f)
        e.integrate(HORIZONTAL, -1)
        assert b.parent.tree == [b, [[d, c, e], f]]
        f.integrate(HORIZONTAL, -1)
        assert root.tree == [a, [b, [d, c, e, f]]]
        b.integrate(VERTICAL, 1)
        assert root.tree == [a, [d, c, e, f, b]]
        a.integrate(HORIZONTAL, 1)
        assert root.tree == [[d, c, e, f, b, a]]

    def test_find_payload(self, root, grid):
        a, b, c, d, e = grid
        assert root.find_payload('a') is a
        assert root.find_payload('b') is b
        assert root.find_payload('d') is d
        assert root.find_payload('x') is None

    def test_last_access(self, root, grid):
        a, b, c, d, e = grid
        f = Node('f')
        a.split_with(f)
        d.access()
        assert b.down is d
        b.access()
        assert f.right is b
        f.access()
        assert b.left is f

    def test_size(self, grid):
        a, b, c, d, e = grid
        assert a.size == a.width == 60
        assert b.size == b.height == 25

    def test_capacity(self, root, grid):
        a, b, c, d, e = grid
        assert root.capacity == 120
        assert b.parent.capacity == 50
        assert c.parent.capacity == 60
        assert c.capacity == 25

    def test_capacity2(self, root):
        a, b, c = Nodes('a b c')
        root.add_child(a)
        root.add_child(b)
        b.split_with(c)

    def test_resize(self, root, grid):
        a, b, c, d, e = grid
        a.grow(10)
        assert a.width == a.size == 70
        assert b.height == b.size == 25
        assert b.width == 50
        assert c.width == d.width == e.width == 50/3
        assert a.pos == (0, 0)
        assert b.pos == (70, 0)
        assert c.pos == (70, 25)
        assert d.pos == (70 + 50/3, 25)
        assert e.pos == (70 + (50/3)*2, 25)
        b.grow(-5)
        assert c.width == d.width == e.width == 50/3
        assert c.height == d.height == e.height == 30
        d.grow(5)
        assert d.width == 50/3 + 5
        d.move_up()
        assert d.size == (50 - b.size) / 2
        b.integrate(VERTICAL, 1)
        assert b.size == d.size == 25
        assert b.parent.size == 25

    def test_resize_absolute(self, root, grid):
        a, b, c, d, e = grid
        b.size = 10
        assert b.size == b.height == 10
        assert c.parent.size == 40
        b.size = 5
        assert b.size == 10

    def test_resize_absolute_and_relative(self, root):
        a, b, c, d = Nodes('a b c d')
        root.add_child(a)
        root.add_child(b)
        a.size = 20
        b.size = 20
        assert a.size == 100
        assert b.size == 20
        root.add_child(c)
        assert c.size == 40
        assert a.size == approx(100 * (2/3))
        assert b.size == approx(20 * (2/3))
        root.add_child(d)
        assert c.size == d.size == 20

    def test_resize_minimum(self, root, grid):
        a, b, c, d, e = grid
        b.grow(-100)
        assert b.size == 10

    def test_resize_all_absolute_underflow(self, root, grid):
        a, b, c, d, e = grid
        c.size = 10
        d.size = 10
        assert e.size == 40
        e.size = 10
        assert e.size == 10
        assert c.size == d.size == 25

    def test_resize_all_absolute_overflow(self, root, grid):
        a, b, c, d, e = grid
        c.size = d.size = 15
        e.size = 40
        assert e.size == 40
        assert c.size == d.size == 10
        e.size = 50
        assert e.size == 40
        assert c.size == d.size == 10

    def test_resize_overflow_with_relative(self, root, grid):
        a, b, c, d, e = grid
        c.size = 20
        d.size = 40
        assert c.size == 10
        assert d.size == 40
        assert e.size == 10
        assert e.autosized
        d.size = 50
        assert c.size == 10
        assert d.size == 40
        assert e.size == 10
        assert e.autosized

    def test_resize_only_absolute_remains(self, root):
        a, b, c = Nodes('a b c')
        root.add_child(a)
        root.add_child(b)
        a.size = 20
        b.size = 20
        root.add_child(c)
        root.remove_child(c)
        info(root)
        assert a.size == 100
        assert b.size == 20

    def test_reset_size(self, grid):
        a, b, c, d, e = grid
        a.grow(5)
        assert a.size == 65
        a.reset_size()
        assert a.size == 60

    def test_size_after_split(self, root):
        a, b, c = Nodes('a b c')
        root.add_child(a)
        root.add_child(b)
        b.grow(-20)
        b.split_with(c)
        assert b.parent.size == 40
        assert b.size == c.size == 25
        b.remove()
        assert c.size == 40

    def test_only_child_must_be_autosized(self, root):
        a, b = Nodes('a b')
        root.add_child(a)
        root.add_child(b)
        a.size = 10
        root.remove_child(b)
        assert a.autosized


    def test_deny_only_child_resize(self, root):
        pass
        # TODO

    def test_resize_parents(self, root):
        a, b, c = Nodes('a b c')
        root.add_child(a)
        root.add_child(b)
        b.split_with(c)
        b.grow(10, HORIZONTAL)
        assert b.parent.size == 70
        assert b.size == c.size == 25

class TestDebugging:

    def test_tree(self, root, grid):
        lines = tree(root).split('\n')
        print(lines)
        assert lines[0].startswith('root')
        assert lines[1].strip().startswith('a')
        assert lines[2].strip().startswith('*')
        assert lines[3].strip().startswith('b')

    def test_draw(self, root, grid):
        a, *_ = grid
        root._width = 24
        root._height = 10
        a.payload = 'XXXXXXXXXXXX'
        data = draw(root)
        assert data == '''
        ┌──────────┐┌──────────┐
        │XXXXXXXXXX││b.........│
        │..........││..........│
        │..........││..........│
        │..........│└──────────┘
        │..........│┌──┐┌──┐┌──┐
        │..........││c.││d.││e.│
        │..........││..││..││..│
        │..........││..││..││..│
        └──────────┘└──┘└──┘└──┘
        '''.replace(' ','')[1:]

    def test_info(self, root, grid, capsys):
        info(root)
        out, _ = capsys.readouterr()
        assert out == tree(root) + '\n' + draw(root) + '\n'
