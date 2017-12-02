from collections import namedtuple


HORIZONTAL = False
VERTICAL = True
MIN_SIZE = 10
ROOT_ORIENT = HORIZONTAL
Dimensions = namedtuple('Dimensions', 'x y width height')

class Node:

    def __init__(self, payload=None, x=None, y=None, width=None, height=None):
        self.payload = payload
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._size = None
        self.children = []
        self.last_accessed = None
        self.parent = None

    def __repr__(self):
        info = self.payload or ''
        if self.children:
            info += ' +%d' % len(self.children)
        return '<Node %s %x>' % (info, id(self))

    @property
    def is_root(self):
        return self.parent is None

    @property
    def index(self):
        return self.parent.children.index(self)

    @property
    def siblings(self):
        return [c for c in self.parent.children if c is not self]

    @property
    def is_leaf(self):
        return len(self.children) == 0

    @property
    def first_leaf(self):
        if self.is_leaf:
            return self
        return self.children[0].first_leaf

    @property
    def last_leaf(self):
        if self.is_leaf:
            return self
        return self.children[-1].last_leaf

    @property
    def recent_leaf(self):
        if self.is_leaf:
            return self
        if self.last_accessed is None:
            return self.children[0].recent_leaf
        return self.last_accessed.recent_leaf

    @property
    def prev_leaf(self):
        if self.is_root:
            return self.last_leaf
        idx = self.index - 1
        if idx < 0:
            return self.parent.prev_leaf
        return self.parent.children[idx].last_leaf

    @property
    def next_leaf(self):
        if self.is_root:
            return self.first_leaf
        idx = self.index + 1
        if idx >= len(self.parent.children):
            return self.parent.next_leaf
        return self.parent.children[idx].first_leaf

    @property
    def orient(self):
        if self.is_root:
            return ROOT_ORIENT
        return not self.parent.orient

    @property
    def horizontal(self):
        return self.orient is HORIZONTAL

    @property
    def vertical(self):
        return self.orient is VERTICAL

    @property
    def tree(self):
        return [x.tree if x.children else x for x in self.children]

    @property
    def size_offset(self):
        return sum(c.size for c in self.parent.children[:self.index])

    @property
    def x(self):
        if self.is_root:
            return self._x
        if self.horizontal:
            return self.parent.x
        return self.parent.x + self.size_offset
    @property
    def y(self):
        if self.is_root:
            return self._y
        if self.vertical:
            return self.parent.y
        return self.parent.y + self.size_offset

    @property
    def pos(self):
        return (self.x, self.y)

    @property
    def width(self):
        if self.is_root:
            return self._width
        if self.horizontal:
            return self.parent.width
        return self.size

    @property
    def height(self):
        if self.is_root:
            return self._height
        if self.vertical:
            return self.parent.height
        return self.size

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
        if self.is_root:
            return None
        if self.fixed:
            return self._size
        # Distribute space evenly among flexible containers
        total = self.parent.capacity
        taken = sum(c.size for c in self.siblings if c.fixed)
        flexibles = [c for c in self.parent.children if c.flexible]
        return (total - taken) / len(flexibles)

    @size.setter
    def size(self, val):
        if len(self.siblings) == 0:
            return
        total = self.parent.capacity
        # Size can't be set smaller than minium or higher than available space
        val = min(total - MIN_SIZE * len(self.siblings), max(MIN_SIZE, val))
        # Space left in container after applying size
        space = total - sum(c.min_size for c in self.siblings) - val
        # If the container overflows, or some space remains but there are no
        # flexible containers to grow into it...
        if space < 0 or not any(c.flexible for c in self.siblings):
            fixed_total = sum(c.size for c in self.siblings if c.fixed)
            # ...shrink/grow all siblings to fill the space
            for sibling in [c for c in self.siblings if c.fixed]:
                sibling._size *= (fixed_total + space) / fixed_total
        self._size = val

    @property
    def flexible(self):
        return self._size is None

    @property
    def fixed(self):
        return self._size is not None

    @property
    def min_size(self):
        return MIN_SIZE if self.flexible else self._size

    def reset_size(self):
        self._size = None

    def grow(self, amt, orient=None):
        if orient is (not self.parent.orient):
            self.parent.grow(amt)
            return
        self.size += amt

    def access(self):
        self.parent.last_accessed = self

    def neighbor(self, orient, direction):
        if self.is_root:
            return None
        if orient is self.parent.orient:
            target_idx = self.index + direction
            if 0 <= target_idx < len(self.parent.children):
                return self.parent.children[target_idx].recent_leaf
            if self.parent.is_root:
                return None
            return self.parent.parent.neighbor(orient, direction)
        return self.parent.neighbor(orient, direction)

    @property
    def up(self):
        return self.neighbor(VERTICAL, -1)

    @property
    def down(self):
        return self.neighbor(VERTICAL, 1)

    @property
    def left(self):
        return self.neighbor(HORIZONTAL, -1)

    @property
    def right(self):
        return self.neighbor(HORIZONTAL, 1)

    def add_child(self, node, idx=None):
        # If has children and each child has absolute size...
        if not self.is_leaf and all(c.fixed for c in self.children):
            num = len(self.children)
            # ...shrink each child to make space for new child
            for child in self.children:
                child._size /= (num + 1) / num
        if idx is None:
            idx = len(self.children)
        self.children.insert(idx, node)
        node.parent = self

    def add_child_after(self, new, old):
        self.add_child(new, idx=self.children.index(old)+1)

    def remove_child(self, node):
        self.children.remove(node)
        if len(self.children) == 0:
            assert self.is_root
            return
        if len(self.children) == 1:
            if not self.is_root:
                # Collapse tree with a single child
                self.parent.replace_child(self, self.children[0])
            else:
                # A single child doesn't need an absolute size
                self.children[0].reset_size()
            return
        # If no flexible children are there to fill empty space...
        if all([c.fixed for c in self.children]):
            # ...grow all children to fill the space
            factor = self.capacity / sum(c.size for c in self.children)
            for child in self.children:
                child._size *= factor

    def remove(self):
        self.parent.remove_child(self)

    def replace_child(self, old, new):
        self.children[self.children.index(old)] = new
        new.parent = self
        new._size = old._size

    def split_with(self, node):
        container = Node()
        self.parent.replace_child(self, container)
        self.reset_size()
        for child in [self, node]:
            container.add_child(child)

    def move(self, orient, direction=1):
        if self.is_root:
            return
        if orient == self.parent.orient:
            old_idx = self.parent.children.index(self)
            new_idx = old_idx + direction
            if 0 <= new_idx < len(self.parent.children):
                ch = self.parent.children
                ch[old_idx], ch[new_idx] = ch[new_idx], ch[old_idx]
                return
            new_sibling = self.parent.parent
        else:
            new_sibling = self.parent
        try:
            new_parent = new_sibling.parent
            idx = new_parent.children.index(new_sibling)
        except AttributeError:
            return
        self.reset_size()
        self.parent.remove_child(self)
        offset = 1 if direction == 1 else 0
        new_parent.add_child(self, idx + offset)

    def move_up(self):
        self.move(VERTICAL, -1)

    def move_down(self):
        self.move(VERTICAL, 1)

    def move_right(self):
        self.move(HORIZONTAL, 1)

    def move_left(self):
        self.move(HORIZONTAL, -1)

    def _move_and_integrate(self, orient, direction):
        old_parent = self.parent
        self.move(orient, direction)
        if self.parent is not old_parent:
            self.integrate(orient, direction)

    def integrate(self, orient, direction):
        if orient != self.parent.orient:
            self._move_and_integrate(orient, direction)
            return
        target_idx = self.parent.children.index(self) + direction
        if target_idx < 0 or target_idx >= len(self.parent.children):
            self._move_and_integrate(orient, direction)
            return
        self.reset_size()
        target = self.parent.children[target_idx]
        self.parent.remove_child(self)
        if len(target.children) == 0:
            target.split_with(self)
        else:
            target.add_child(self)

    def integrate_up(self):
        self.integrate(VERTICAL, -1)

    def integrate_down(self):
        self.integrate(VERTICAL, 1)

    def integrate_left(self):
        self.integrate(HORIZONTAL, -1)

    def integrate_right(self):
        self.integrate(HORIZONTAL, 1)

    def find_payload(self, payload):
        if self.payload is payload:
            return self
        for node in self.children:
            needle = node.find_payload(payload)
            if needle:
                return needle
