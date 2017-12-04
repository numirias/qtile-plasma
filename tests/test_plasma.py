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
        assert n.size is None
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
        root.remove_child(b)
        assert root.children == []

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
        assert a.next_leaf == b
        assert b.next_leaf == c
        assert c.next_leaf == d
        assert d.next_leaf == e
        assert e.next_leaf == a
        assert a.prev_leaf == e
        assert e.prev_leaf == d
        assert d.prev_leaf == c
        assert c.prev_leaf == b
        assert b.prev_leaf == a

    def test_siblings(self, grid):
        a, b, c, d, e = grid
        assert d.siblings == [c, e]
        assert b.siblings == [c.parent]

    def test_move_forward(self, root, grid):
        a, b, c, d, e = grid
        assert c.parent.children == [c, d, e]
        c.move_right()
        assert c.parent.children == [d, c, e]
        c.move_right()
        assert c.parent.children == [d, e, c]
        c.move_right()
        assert root.tree == [a, [b, [d, e]], c]

    def test_move_backward(self, root, grid):
        a, b, c, d, e = grid
        e.move_left()
        assert c.parent.children == [c, e, d]
        e.move_left()
        assert c.parent.children == [e, c, d]
        e.move_left()
        assert root.tree == [a, e, [b, [c, d]]]

    def test_advanced_move(self, grid):
        a, b, c, d, e = grid
        c.move_up()
        assert b.parent.tree == [b, c, [d, e]]
        a.move_up()
        assert b.parent.tree == [b, c, [d, e]]

    def test_advanced_move2(self, root, grid):
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

    def test_move_blocked(self, root, grid):
        a, b, c, d, e = grid
        orig_tree = root.tree.copy()
        a.move_up()
        assert root.tree == orig_tree
        b.move_up()
        assert root.tree == orig_tree
        b.move_right()

    def test_move_root(self, root):
        a = Node('a')
        root.add_child(a)
        root.move_up()
        assert root.tree == [a]

    def test_integrate(self, root):
        a, b, c, d, e = Nodes('a b c d e')
        root.add_child(a)
        root.add_child(b)
        root.add_child(c)
        root.add_child(d)
        c.integrate_left()
        assert root.tree == [a, [b, c], d]
        a.integrate_right()
        assert root.tree == [[b, c, a], d]
        a.parent.add_child(e)
        c.integrate_down()
        assert root.tree == [[b, [a, c], e], d]
        e.integrate_up()
        assert root.tree == [[b, [a, c, e]], d]

    def test_integrate_nested(self, root, grid):
        a, b, c, d, e = grid
        c.integrate_right()
        assert root.tree == [a, [b, [[d, c], e]]]

    def test_move_and_integrate(self, root, grid):
        a, b, c, d, e = grid
        c.integrate_left()
        assert root.tree == [[a, c], [b, [d, e]]]
        a.integrate_right()
        assert root.tree == [c, [b, [d, e], a]]
        d.integrate_down()
        assert root.tree == [c, [b, e, [a, d]]]
        a.integrate_up()
        assert root.tree == [c, [b, [e, a], d]]
        e.integrate_left()
        assert root.tree == [[c, e], [b, a, d]]
        f = Node('f')
        a.split_with(f)
        g = Node('g')
        a.split_with(g)
        g.integrate_left()
        assert root.tree == [[c, e, g], [b, [a, f], d]]

    def test_impossible_integrate(self, root, grid):
        a, b, c, d, e = grid
        orig_tree = root.tree.copy()
        a.integrate_left()
        assert orig_tree == root.tree
        b.integrate_up()
        assert orig_tree == root.tree

    def test_impossible_integrate2(self, root):
        a, b = Nodes('a b')
        root.add_child(a)
        root.add_child(b)
        orig_tree = root.tree.copy()
        b.integrate_up()
        assert root.tree == orig_tree
        b.integrate_down()
        assert root.tree == orig_tree
        b.integrate_right()
        assert root.tree == orig_tree
        a.integrate_up()
        assert root.tree == orig_tree
        a.integrate_down()
        assert root.tree == orig_tree
        a.integrate_left()
        assert root.tree == orig_tree

    def test_find_payload(self, root, grid):
        a, b, c, d, e = grid
        assert root.find_payload('a') is a
        assert root.find_payload('b') is b
        assert root.find_payload('d') is d
        assert root.find_payload('x') is None

    def test_last_access(self, grid):
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
        b.integrate_down()
        assert b.size == d.size == 25
        assert b.parent.size == 25

    def test_resize_absolute(self, grid):
        a, b, c, d, e = grid
        b.size = 10
        assert b.size == b.height == 10
        assert c.parent.size == 40
        b.size = 5
        assert b.size == 10

    def test_resize_absolute2(self, root):
        a, b, c = Nodes('a b c')
        root.add_child(a)
        root.add_child(b)
        root.add_child(c)
        a.size = 30
        b.size = 60
        c.size = 40
        assert a.size == 30 * (80/90)
        assert b.size == 60 * (80/90)
        assert c.size == 40

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

    def test_resize_absolute_and_relative2(self, root):
        a, b, c = Nodes('a b c')
        root.add_child(a)
        root.add_child(b)
        root.add_child(c)
        a.grow(10)
        assert a.size == 50
        assert b.size == 35
        assert c.size == 35
        b.grow(10)
        assert a.size == 50
        assert b.size == 45
        assert c.size == 25

    def test_resize_minimum(self, grid):
        a, b, c, d, e = grid
        b.grow(-100)
        assert b.size == 10

    def test_resize_all_absolute_underflow(self, grid):
        a, b, c, d, e = grid
        c.size = 10
        d.size = 10
        assert e.size == 40
        e.size = 10
        assert e.size == 10
        assert c.size == d.size == 25

    def test_resize_all_absolute_overflow(self, grid):
        a, b, c, d, e = grid
        c.size = d.size = 15
        e.size = 40
        assert e.size == 40
        assert c.size == d.size == 10
        e.size = 50
        assert e.size == 40
        assert c.size == d.size == 10

    def test_resize_overflow_with_relative(self, grid):
        a, b, c, d, e = grid
        c.size = 20
        d.size = 40
        assert c.size == 10
        assert d.size == 40
        assert e.size == 10
        assert e.flexible
        d.size = 50
        assert c.size == 10
        assert d.size == 40
        assert e.size == 10
        assert e.flexible

    def test_resize_only_absolute_remains(self, root):
        a, b, c = Nodes('a b c')
        root.add_child(a)
        root.add_child(b)
        a.size = 20
        b.size = 20
        root.add_child(c)
        root.remove_child(c)
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

    def test_only_child_must_be_flexible(self, root):
        a, b = Nodes('a b')
        root.add_child(a)
        root.add_child(b)
        a.size = 10
        root.remove_child(b)
        assert a.flexible

    def test_deny_only_child_resize(self, root):
        a = Node('a')
        root.add_child(a)
        a.size = 10
        assert a.size == 120

    def test_resize_parents(self, root):
        a, b, c = Nodes('a b c')
        root.add_child(a)
        root.add_child(b)
        b.split_with(c)
        b.grow(10, HORIZONTAL)
        assert b.parent.size == 70
        assert b.size == c.size == 25

    def test_pixelperfect(self, root, tiny_grid):
        a, b, c = tiny_grid
        root._height = 11
        root._width = 11
        ds = a.pixel_perfect
        assert all(type(x) is int for x in (ds.x, ds.y, ds.width, ds.height))
        assert a.width + b.width == 11
        assert a.pixel_perfect.width + b.pixel_perfect.width == 11
        assert b.height + c.height == 11
        assert b.pixel_perfect.height + c.pixel_perfect.height == 11

    def test_pixelperfect_draw(self, root, complex_grid):
        root._height = 10
        for i in range(40, 50):
            root._width = i
            view = draw(root)
            assert '#' not in view
        root._width = 50
        for i in range(10, 20):
            root._height = i
            view = draw(root)
            assert '#' not in view

    def test_resize_root(self, root):
        a, b, c = Nodes('a b c')
        root.add_child(a)
        root.add_child(b)
        a.grow(10, orient=VERTICAL)
        root.grow(10, orient=VERTICAL)
        root.grow(10, orient=HORIZONTAL)
        root.size = 10
        assert a._size is b._size is root._size is None

    def test_set_xy(self, root, tiny_grid):
        a, b, c = tiny_grid
        root.x = 10
        root.y = 20
        assert root.x == 10
        assert root.y == 20
        a.x = 30
        a.y = 40
        assert a.x == root.x == 10
        assert a.y == root.y == 20
        root.width = 50
        root.height = 60
        assert root._width == 50
        assert root._height == 60

    def test_set_width_height(self, root, tiny_grid):
        a, b, c = tiny_grid
        a.width = 70
        assert a.width == 70
        assert b.width == c.width == 50
        b.height = 30
        assert b.height == 30
        assert c.height == 20
        b.width = 80
        assert b.width == c.width == 80
        assert a.width == 40
        a.height = 20
        assert a.height == 50

    def test_grow_directions(self, root, grid):
        a, b, c, d, e = grid
        # TODO

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
        '''.replace(' ', '')[1:]

    def test_info(self, root, grid, capsys):
        info(root)
        out, _ = capsys.readouterr()
        assert out == tree(root) + '\n' + draw(root) + '\n'
