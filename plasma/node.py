
HORIZONTAL = False
VERTICAL = True

class Node:

    def __init__(self, payload=None, x=None, y=None, width=None, height=None, default_orient=HORIZONTAL, parent=None):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._size = None
        self._default_orient = default_orient
        self.last_accessed = None
        self.payload = payload
        self.parent = parent
        self.children = []

    def __repr__(self):
        if self.payload is None:
            info = '+%d' % len(self.children)
        else:
            info = self.payload
        return '<Node %s %x>' % (info, id(self))

    @property
    def x(self):
        if self.is_root:
            return self._x
        if self.parent.vertical:
            return self.parent.x
        return self.parent.x + sum([c.width for c in self.parent.children[:self.index]])

    @property
    def y(self):
        if self.is_root:
            return self._y
        if self.parent.horizontal:
            return self.parent.y
        return self.parent.y + sum([c.height for c in self.parent.children[:self.index]])

    @property
    def pos(self):
        return (self.x, self.y)

    @property
    def width(self):
        if self.is_root:
            return self._width
        if self.parent.vertical:
            return self.parent.width
        return self.rel_size

    @property
    def height(self):
        if self.is_root:
            return self._height
        if self.parent.horizontal:
            return self.parent.height
        return self.rel_size

    @property
    def capacity(self):
        return self.width if self.horizontal else self.height

    @property
    def size(self):
        return self.width if self.vertical else self.height

    @size.setter
    def size(self, val):
        # TODO Simplify
        val = max(10, val)
        max_take = self.parent.capacity - 10 * len(self.siblings)
        val = min(max_take, val)
        sized_siblings = [c for c in self.siblings if not c.autosized]
        autosized_siblings = [c for c in self.siblings if c.autosized]

        space_to_fill = self.parent.capacity - (10 * len(autosized_siblings)) - val - sum(c.size for c in sized_siblings)

        if space_to_fill < sum(c.size for c in sized_siblings) or all(not c.autosized for c in self.siblings):
            for sibling in sized_siblings:
                sibling._size += space_to_fill / len(sized_siblings)
        self._size = val

    @property
    def autosized(self):
        return self._size is None

    @property
    def rel_size(self):
        if not self.autosized:
            return self._size
        if self.parent.horizontal:
            available = self.parent.width
        else:
            available = self.parent.height
        space = available - sum(c.size for c in self.siblings if not c.autosized)
        return space / len([c for c in self.parent.children if c.autosized])

    def grow(self, amt, orient=None):
        if orient is (not self.parent.orient):
            self.parent.grow(amt)
            return
        self.size = self.size + amt

    @property
    def has_parent(self):
        return self.parent is not None

    @property
    def index(self):
        return self.parent.children.index(self)

    @property
    def siblings(self):
        return [c for c in self.parent.children if c is not self]

    @property
    def is_root(self):
        return self.parent is None

    @property
    def is_leaf(self):
        return len(self.children) == 0

    @property
    def recent_leaf(self):
        if self.is_leaf:
            return self
        if self.last_accessed is None:
            return self.children[0].recent_leaf
        return self.last_accessed.recent_leaf

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
    def prev(self):
        if self.is_root:
            return self.last_leaf
        idx = self.index - 1
        if idx < 0:
            return self.parent.prev
        return self.parent.children[idx].last_leaf

    @property
    def next(self):
        if self.is_root:
            return self.first_leaf
        idx = self.index + 1
        if idx >= len(self.parent.children):
            return self.parent.next
        return self.parent.children[idx].first_leaf

    @property
    def orient(self):
        if self.has_parent:
            return not self.parent.orient
        return self._default_orient

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

    def access(self):
        self.parent.last_accessed = self

    def neighbor(self, orient, direction):
        if self.is_root:
            return None
        if orient == self.parent.orient:
            target_idx = self.index + direction
            if 0 <= target_idx < len(self.parent.children):
                return self.parent.children[target_idx].recent_leaf
            if self.parent.is_root:
                return None
            return self.parent.parent.neighbor(orient, direction)
        else:
            return self.parent.neighbor(orient, direction)

    def add_child(self, node, idx=None):
        # If has children and each child has absolute size...
        if not self.is_leaf and all(not c.autosized for c in self.children):
            num = len(self.children)
            # ...shrink each child to make space for new child.
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
        if len(self.children) == 1:
            if not self.is_root:
                # Collapse tree with a single child
                self.parent.replace_child(self, self.children[0])
            else:
                # A single child doesn't need an absolute size
                self.children[0].reset_size()
            return
        # If no autosized children are there to fill empty space...
        if all([not c.autosized for c in self.children]):
            # ...enlarge all children to fill the void.
            factor = self.capacity / sum([c.size for c in self.children])
            for child in self.children:
                child._size *= factor

    def remove(self):
        self.parent.remove_child(self)

    def replace_child(self, old, new):
        self.children[self.children.index(old)] = new
        new.parent = self
        new._size = old._size

    def insert_child(self, idx, node):
        self.children.insert(idx, node)
        node.parent = self

    def split_with(self, node):
        original_parent = self.parent
        container = Node()
        original_parent.replace_child(self, container)
        self.reset_size()
        for child in [self, node]:
            container.add_child(child)

    def move(self, orient, direction=1):
        if orient == self.parent.orient:
            old_idx = self.parent.children.index(self)
            new_idx = old_idx + direction
            if new_idx < 0 or new_idx >= len(self.parent.children):
                return
            ch = self.parent.children
            ch[old_idx], ch[new_idx] = ch[new_idx], ch[old_idx]
        else:
            self.reset_size()
            pparent = self.parent.parent
            if pparent is None:
                return
            target_idx = pparent.children.index(self.parent)
            self.parent.remove_child(self)
            offset = 1 if direction == 1 else 0
            pparent.insert_child(target_idx + offset, self)

    def move_left(self):
        self.move(HORIZONTAL, -1)

    def move_up(self):
        self.move(VERTICAL, -1)

    def move_right(self):
        self.move(HORIZONTAL, 1)

    def move_down(self):
        self.move(VERTICAL, 1)

    def integrate(self, orient, direction=1):
        if orient != self.parent.orient:
            return
        target_idx = self.parent.children.index(self) + direction
        if target_idx < 0 or target_idx >= len(self.parent.children):
            return
        self.reset_size()
        target = self.parent.children[target_idx]
        self.parent.remove_child(self)
        if len(target.children) == 0:
            target.split_with(self)
        else:
            target.add_child(self)

    def reset_size(self):
        self._size = None

    def find_payload(self, payload):
        if self.payload is payload:
            return self
        for node in self.children:
            needle = node.find_payload(payload)
            if needle:
                return needle
