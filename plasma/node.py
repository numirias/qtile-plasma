from collections import namedtuple
import time
from math import isclose
import sys

if sys.version_info >= (3, 6):
    from enum import Enum, Flag, auto
else:
    # Python 3.5 backport
    from .enum import Enum, Flag, auto


Point = namedtuple('Point', 'x y')
Dimensions = namedtuple('Dimensions', 'x y width height')

class Orient(Flag):
    HORIZONTAL = 0
    VERTICAL = 1

HORIZONTAL = Orient.HORIZONTAL
VERTICAL   = Orient.VERTICAL

class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    @property
    def orient(self):
        return HORIZONTAL if self in [self.LEFT, self.RIGHT] else VERTICAL

    @property
    def offset(self):
        return 1 if self in [self.RIGHT, self.DOWN] else -1

UP    = Direction.UP
DOWN  = Direction.DOWN
LEFT  = Direction.LEFT
RIGHT = Direction.RIGHT

class AddMode(Flag):
    HORIZONTAL = 0
    VERTICAL = 1
    SPLIT = auto()

    @property
    def orient(self):
        return VERTICAL if self & self.VERTICAL else HORIZONTAL

border_check = {
    UP: lambda a, b: isclose(a.y, b.y_end),
    DOWN: lambda a, b: isclose(a.y_end, b.y),
    LEFT: lambda a, b: isclose(a.x, b.x_end),
    RIGHT: lambda a, b: isclose(a.x_end, b.x),
}

class NotRestorableError(Exception):
    pass

class Node:
    """A tree node.

    Each node represents a container that can hold a payload and child nodes.
    """
    min_size_default = 100
    root_orient = HORIZONTAL

    def __init__(self, payload=None, x=None, y=None, width=None, height=None):
        self.payload = payload
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._size = None
        self.children = []
        self.last_accessed = 0
        self.parent = None
        self.restorables = {}

    def __repr__(self):
        info = self.payload or ''
        if self:
            info += ' +%d' % len(self)
        return '<Node %s %x>' % (info, id(self))

    def __contains__(self, node):
        if node is self:
            return True
        for child in self:
            if node in child:
                return True
        return False

    def __iter__(self):
        yield from self.children

    def __getitem__(self, key):
        return self.children[key]

    def __setitem__(self, key, value):
        self.children[key] = value

    def __len__(self):
        return len(self.children)

    @property
    def root(self):
        try:
            return self.parent.root
        except AttributeError:
            return self

    @property
    def is_root(self):
        return self.parent is None

    @property
    def is_leaf(self):
        return not self

    @property
    def index(self):
        return self.parent.children.index(self)

    @property
    def tree(self):
        return [c.tree if c else c for c in self]

    @property
    def siblings(self):
        return [c for c in self.parent if c is not self]

    @property
    def first_leaf(self):
        if self.is_leaf:
            return self
        return self[0].first_leaf

    @property
    def last_leaf(self):
        if self.is_leaf:
            return self
        return self[-1].last_leaf

    @property
    def recent_leaf(self):
        if self.is_leaf:
            return self
        return max(self, key=lambda n: n.last_accessed).recent_leaf

    @property
    def prev_leaf(self):
        if self.is_root:
            return self.last_leaf
        idx = self.index - 1
        if idx < 0:
            return self.parent.prev_leaf
        return self.parent[idx].last_leaf

    @property
    def next_leaf(self):
        if self.is_root:
            return self.first_leaf
        idx = self.index + 1
        if idx >= len(self.parent):
            return self.parent.next_leaf
        return self.parent[idx].first_leaf

    @property
    def all_leafs(self):
        if self.is_leaf:
            yield self
        for child in self:
            yield from child.all_leafs

    @property
    def orient(self):
        if self.is_root:
            return self.root_orient
        return ~self.parent.orient

    @property
    def horizontal(self):
        return self.orient is HORIZONTAL

    @property
    def vertical(self):
        return self.orient is VERTICAL

    @property
    def x(self):
        if self.is_root:
            return self._x
        if self.horizontal:
            return self.parent.x
        return self.parent.x + self.size_offset

    @x.setter
    def x(self, val):
        if not self.is_root:
            return
        self._x = val

    @property
    def y(self):
        if self.is_root:
            return self._y
        if self.vertical:
            return self.parent.y
        return self.parent.y + self.size_offset

    @y.setter
    def y(self, val):
        if not self.is_root:
            return
        self._y = val

    @property
    def pos(self):
        return Point(self.x, self.y)

    @property
    def width(self):
        if self.is_root:
            return self._width
        if self.horizontal:
            return self.parent.width
        return self.size

    @width.setter
    def width(self, val):
        if self.is_root:
            self._width = val
        elif self.horizontal:
            self.parent.size = val
        else:
            self.size = val

    @property
    def height(self):
        if self.is_root:
            return self._height
        if self.vertical:
            return self.parent.height
        return self.size

    @height.setter
    def height(self, val):
        if self.is_root:
            self._height = val
        elif self.vertical:
            self.parent.size = val
        else:
            self.size = val

    @property
    def x_end(self):
        return self.x + self.width

    @property
    def y_end(self):
        return self.y + self.height

    @property
    def x_center(self):
        return self.x + self.width / 2

    @property
    def y_center(self):
        return self.y + self.height / 2

    @property
    def center(self):
        return Point(self.x_center, self.y_center)

    @property
    def top_left(self):
        return Point(self.x, self.y)

    @property
    def top_right(self):
        return Point(self.x + self.width, self.y)

    @property
    def bottom_left(self):
        return Point(self.x, self.y + self.height)

    @property
    def bottom_right(self):
        return Point(self.x + self.width, self.y + self.height)

    @property
    def pixel_perfect(self):
        """Return pixel-perfect int dimensions (x, y, width, height) which
        compensate for gaps in the layout grid caused by plain int conversion.
        """
        x, y, width, height = self.x, self.y, self.width, self.height
        threshold = 0.99999
        if (x - int(x)) + (width - int(width)) > threshold:
            width += 1
        if (y - int(y)) + (height - int(height)) > threshold:
            height += 1
        return Dimensions(*map(int, (x, y, width, height)))

    @property
    def capacity(self):
        return self.width if self.horizontal else self.height

    @property
    def size(self):
        """Return amount of space taken in parent container."""
        if self.is_root:
            return None
        if self.fixed:
            return self._size
        if self.flexible:
            # Distribute space evenly among flexible nodes
            taken = sum(n.size for n in self.siblings if not n.flexible)
            flexibles = [n for n in self.parent if n.flexible]
            return (self.parent.capacity - taken) / len(flexibles)
        return max(sum(gc.min_size for gc in c) for c in self)

    @size.setter
    def size(self, val):
        if self.is_root or not self.siblings:
            return
        if val is None:
            self.reset_size()
            return
        occupied = sum(s.min_size_bound for s in self.siblings)
        val = max(min(val, self.parent.capacity - occupied),
                  self.min_size_bound)
        self.force_size(val)

    def force_size(self, val):
        """Set size without considering available space."""
        Node.fit_into(self.siblings, self.parent.capacity - val)
        if val == 0:
            return
        if self:
            Node.fit_into([self], val)
        self._size = val

    @property
    def size_offset(self):
        return sum(c.size for c in self.parent[:self.index])

    @staticmethod
    def fit_into(nodes, space):
        """Resize nodes to fit them into the available space."""
        if not nodes:
            return
        occupied = sum(n.min_size for n in nodes)
        if space >= occupied and any(n.flexible for n in nodes):
            # If any flexible node exists, it will occupy the space
            # automatically, not requiring any action.
            return
        nodes_left = nodes[:]
        space_left = space
        if space < occupied:
            for node in nodes:
                if node.min_size_bound != node.min_size:
                    continue
                # Substract nodes that are already at their minimal possible
                # size because they can't be shrinked any further.
                space_left -= node.min_size
                nodes_left.remove(node)
        if not nodes_left:
            return
        factor = space_left / sum(n.size for n in nodes_left)
        for node in nodes_left:
            new_size = node.size * factor
            if node.fixed:
                node._size = new_size  # pylint: disable=protected-access
            for child in node:
                Node.fit_into(child, new_size)

    @property
    def fixed(self):
        """A node is fixed if it has a specified size."""
        return self._size is not None

    @property
    def min_size(self):
        if self.fixed:
            return self._size
        if self.is_leaf:
            return self.min_size_default
        size = max(sum(gc.min_size for gc in c) for c in self)
        return max(size, self.min_size_default)

    @property
    def min_size_bound(self):
        if self.is_leaf:
            return self.min_size_default
        return max(sum(gc.min_size_bound for gc in c) or
                   self.min_size_default for c in self)

    def reset_size(self):
        self._size = None

    @property
    def flexible(self):
        """A node is flexible if its size isn't (explicitly or implictly)
        determined.
        """
        if self.fixed:
            return False
        return all((any(gc.flexible for gc in c) or c.is_leaf) for c in self)

    def access(self):
        self.last_accessed = time.time()
        try:
            self.parent.access()
        except AttributeError:
            pass

    def neighbor(self, direction):
        """Return adjacent leaf node in specified direction."""
        if self.is_root:
            return None
        if direction.orient is self.parent.orient:
            target_idx = self.index + direction.offset
            if 0 <= target_idx < len(self.parent):
                return self.parent[target_idx].recent_leaf
            if self.parent.is_root:
                return None
            return self.parent.parent.neighbor(direction)
        return self.parent.neighbor(direction)

    @property
    def up(self):
        return self.neighbor(UP)

    @property
    def down(self):
        return self.neighbor(DOWN)

    @property
    def left(self):
        return self.neighbor(LEFT)

    @property
    def right(self):
        return self.neighbor(RIGHT)

    def common_border(self, node, direction):
        """Return whether a common border with given node in specified
        direction exists.
        """
        if not border_check[direction](self, node):
            return False
        if direction in [UP, DOWN]:
            detached = node.x >= self.x_end or node.x_end <= self.x
        else:
            detached = node.y >= self.y_end or node.y_end <= self.y
        return not detached

    def close_neighbor(self, direction):
        """Return visually adjacent leaf node in specified direction."""
        nodes = [n for n in self.root.all_leafs if
                 self.common_border(n, direction)]
        if not nodes:
            return None
        most_recent = max(nodes, key=lambda n: n.last_accessed)
        if most_recent.last_accessed > 0:
            return most_recent
        if direction in [UP, DOWN]:
            match = lambda n: n.x <= self.x_center <= n.x_end
        else:
            match = lambda n: n.y <= self.y_center <= n.y_end
        return next(n for n in nodes if match(n))

    @property
    def close_up(self):
        return self.close_neighbor(UP)

    @property
    def close_down(self):
        return self.close_neighbor(DOWN)

    @property
    def close_left(self):
        return self.close_neighbor(LEFT)

    @property
    def close_right(self):
        return self.close_neighbor(RIGHT)

    def add_child(self, node, idx=None):
        if idx is None:
            idx = len(self)
        self.children.insert(idx, node)
        node.parent = self
        if len(self) == 1:
            return
        total = self.capacity
        Node.fit_into(node.siblings, total - (total / len(self)))

    def add_child_after(self, new, old):
        self.add_child(new, idx=old.index+1)

    def remove_child(self, node):
        node._save_restore_state()  # pylint: disable=W0212
        node.force_size(0)
        self.children.remove(node)
        if len(self) == 1:
            child = self[0]
            if self.is_root:
                # A single child doesn't need a fixed size
                child.reset_size()
            else:
                # Collapse tree with a single child
                self.parent.replace_child(self, child)
                Node.fit_into(child, self.capacity)

    def remove(self):
        self.parent.remove_child(self)

    def replace_child(self, old, new):
        self[old.index] = new
        new.parent = self
        new._size = old._size  # pylint: disable=protected-access

    def flip_with(self, node, reverse=False):
        """Join with node in a new, orthogonal container."""
        container = Node()
        self.parent.replace_child(self, container)
        self.reset_size()
        for child in [node, self] if reverse else [self, node]:
            container.add_child(child)

    def add_node(self, node, mode=None):
        """Add node according to the mode.

        This can result in adding it as a child, joining with it in a new
        flipped sub-container, or splitting the space with it.
        """
        if self.is_root:
            self.add_child(node)
        elif mode is None:
            self.parent.add_child_after(node, self)
        elif mode.orient is self.parent.orient:
            if mode & AddMode.SPLIT:
                node._size = 0   # pylint: disable=protected-access
                self.parent.add_child_after(node, self)
                self._size = node._size = self.size / 2
            else:
                self.parent.add_child_after(node, self)
        else:
            self.flip_with(node)

    def restore(self, node):
        """Restore node.

        Try to add the node in a place where a node with the same payload
        has previously been.
        """
        restorables = self.root.restorables
        try:
            parent, idx, sizes, fixed, flip = restorables[node.payload]
        except KeyError:
            raise NotRestorableError()  # pylint: disable=raise-missing-from
        if parent not in self.root:
            # Don't try to restore if parent is not part of the tree anymore
            raise NotRestorableError()
        node.reset_size()
        if flip:
            old_parent_size = parent.size
            parent.flip_with(node, reverse=(idx == 0))
            node.size, parent.size = sizes
            Node.fit_into(parent, old_parent_size)
        else:
            parent.add_child(node, idx=idx)
            node.size = sizes[0]
            if len(sizes) == 2:
                node.siblings[0].size = sizes[1]
        if not fixed:
            node.reset_size()
        del restorables[node.payload]

    def _save_restore_state(self):
        parent = self.parent
        sizes = (self.size,)
        flip = False
        if len(self.siblings) == 1:
            # If there is only one node left in the container, we need to save
            # its size too because the size will be lost.
            sizes += (self.siblings[0]._size,)  # pylint: disable=W0212
            if not self.parent.is_root:
                flip = True
                parent = self.siblings[0]
        self.root.restorables[self.payload] = (parent, self.index, sizes,
                                               self.fixed, flip)

    def move(self, direction):
        """Move this node in `direction`. Return whether node was moved."""
        if self.is_root:
            return False
        if direction.orient is self.parent.orient:
            old_idx = self.index
            new_idx = old_idx + direction.offset
            if 0 <= new_idx < len(self.parent):
                p = self.parent
                p[old_idx], p[new_idx] = p[new_idx], p[old_idx]
                return True
            new_sibling = self.parent.parent
        else:
            new_sibling = self.parent
        try:
            new_parent = new_sibling.parent
            idx = new_sibling.index
        except AttributeError:
            return False
        self.reset_size()
        self.parent.remove_child(self)
        new_parent.add_child(self, idx + (1 if direction.offset == 1 else 0))
        return True

    def move_up(self):
        return self.move(UP)

    def move_down(self):
        return self.move(DOWN)

    def move_right(self):
        return self.move(RIGHT)

    def move_left(self):
        return self.move(LEFT)

    def _move_and_integrate(self, direction):
        old_parent = self.parent
        self.move(direction)
        if self.parent is not old_parent:
            self.integrate(direction)

    def integrate(self, direction):
        if direction.orient != self.parent.orient:
            self._move_and_integrate(direction)
            return
        target_idx = self.index + direction.offset
        if target_idx < 0 or target_idx >= len(self.parent):
            self._move_and_integrate(direction)
            return
        self.reset_size()
        target = self.parent[target_idx]
        self.parent.remove_child(self)
        if target.is_leaf:
            target.flip_with(self)
        else:
            target.add_child(self)

    def integrate_up(self):
        self.integrate(UP)

    def integrate_down(self):
        self.integrate(DOWN)

    def integrate_left(self):
        self.integrate(LEFT)

    def integrate_right(self):
        self.integrate(RIGHT)

    def find_payload(self, payload):
        if self.payload is payload:
            return self
        for child in self:
            needle = child.find_payload(payload)
            if needle is not None:
                return needle
        return None
