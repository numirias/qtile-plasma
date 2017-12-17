import copy

from xcffib.xproto import StackMode
from libqtile.layout.base import Layout

from .node import Node, AddMode, NotRestorableError


class Plasma(Layout):
    """A flexible tree-based layout.

    Each tree node represents a container whose children are aligned either
    horizontally or vertically. Each window is attached to a leaf of the tree
    and takes either a calculated relative amount or a custom absolute amount
    of space in its parent container. Windows can be resized, rearranged and
    integrated into other containers.
    """
    defaults = [
        ('name', 'Plasma', 'Layout name'),
        ('border_normal', '#333333', 'Unfocused window border color'),
        ('border_focus', '#00e891', 'Focused window border color'),
        ('border_normal_fixed', '#333333',
         'Unfocused fixed-size window''border color'),
        ('border_focus_fixed', '#00e8dc',
         'Focused fixed-size window border color'),
        ('border_width', 1, 'Border width'),
        ('border_width_single', 0, 'Border width for single window'),
        ('margin', 0, 'Layout margin'),
    ]

    def __init__(self, **config):
        Layout.__init__(self, **config)
        self.add_defaults(Plasma.defaults)
        self.root = Node()
        self.focused = None
        self.add_mode = None

    @staticmethod
    def convert_names(tree):
        return [Plasma.convert_names(n) if isinstance(n, list) else
                n.payload.name for n in tree]

    @property
    def focused_node(self):
        return self.root.find_payload(self.focused)

    def info(self):
        info = super().info()
        info['tree'] = self.convert_names(self.root.tree)
        return info

    def clone(self, group):
        clone = copy.copy(self)
        clone.group = group
        clone.root = Node()
        clone.focused = None
        clone.add_mode = None
        return clone

    def add(self, client):
        node = self.root if self.focused_node is None else self.focused_node
        new = Node(client)
        try:
            self.root.restore(new)
        except NotRestorableError:
            node.add_node(new, self.add_mode)
        self.add_mode = None

    def remove(self, client):
        self.root.find_payload(client).remove()

    def configure(self, client, screen):
        self.root.x = screen.x
        self.root.y = screen.y
        self.root.width = screen.width
        self.root.height = screen.height
        node = self.root.find_payload(client)
        border_width = self.border_width_single if self.root.tree == [node] \
            else self.border_width
        border_color = getattr(self, 'border_' +
                               ('focus' if client.has_focus else 'normal') +
                               ('' if node.flexible else '_fixed'))
        x, y, width, height = node.pixel_perfect
        client.place(
            x,
            y,
            width-2*border_width,
            height-2*border_width,
            border_width,
            self.group.qtile.colorPixel(border_color),
            margin=self.margin,
        )
        # Always keep tiles below floating windows
        client.window.configure(stackmode=StackMode.Below)
        client.unhide()

    def focus(self, client):
        self.focused = client
        self.root.find_payload(client).access()

    def focus_first(self):
        return self.root.first_leaf.payload

    def focus_last(self):
        return self.root.last_leaf.payload

    def focus_next(self, win):
        next_leaf = self.root.find_payload(win).next_leaf
        return None if next_leaf is self.root.first_leaf else next_leaf.payload

    def focus_previous(self, win):
        prev_leaf = self.root.find_payload(win).prev_leaf
        return None if prev_leaf is self.root.last_leaf else prev_leaf.payload

    def focus_node(self, node):
        if node is None:
            return
        self.group.focus(node.payload)

    def refocus(self):
        self.group.focus(self.focused)

    def cmd_next(self):
        """Focus next window."""
        self.focus_node(self.focused_node.next_leaf)

    def cmd_previous(self):
        """Focus previous window."""
        self.focus_node(self.focused_node.prev_leaf)

    def cmd_recent(self):
        """Focus most recently focused window.

        (Toggles between the two latest active windows.)
        """
        nodes = [n for n in self.root.all_leafs if n is not self.focused_node]
        most_recent = max(nodes, key=lambda n: n.last_accessed)
        self.focus_node(most_recent)

    def cmd_left(self):
        """Focus window to the left."""
        self.focus_node(self.focused_node.close_left)

    def cmd_right(self):
        """Focus window to the right."""
        self.focus_node(self.focused_node.close_right)

    def cmd_up(self):
        """Focus window above."""
        self.focus_node(self.focused_node.close_up)

    def cmd_down(self):
        """Focus window below."""
        self.focus_node(self.focused_node.close_down)

    def cmd_move_left(self):
        """Move current window left."""
        self.focused_node.move_left()
        self.refocus()

    def cmd_move_right(self):
        """Move current window right."""
        self.focused_node.move_right()
        self.refocus()

    def cmd_move_up(self):
        """Move current window up."""
        self.focused_node.move_up()
        self.refocus()

    def cmd_move_down(self):
        """Move current window down."""
        self.focused_node.move_down()
        self.refocus()

    def cmd_integrate_left(self):
        """Integrate current window left."""
        self.focused_node.integrate_left()
        self.refocus()

    def cmd_integrate_right(self):
        """Integrate current window right."""
        self.focused_node.integrate_right()
        self.refocus()

    def cmd_integrate_up(self):
        """Integrate current window up."""
        self.focused_node.integrate_up()
        self.refocus()

    def cmd_integrate_down(self):
        """Integrate current window down."""
        self.focused_node.integrate_down()
        self.refocus()

    def cmd_mode_horizontal(self):
        """Next window will be added horizontally."""
        self.add_mode = AddMode.HORIZONTAL

    def cmd_mode_vertical(self):
        """Next window will be added vertically."""
        self.add_mode = AddMode.VERTICAL

    def cmd_mode_horizontal_split(self):
        """Next window will be added horizontally, splitting space of current
        window.
        """
        self.add_mode = AddMode.HORIZONTAL | AddMode.SPLIT

    def cmd_mode_vertical_split(self):
        """Next window will be added vertically, splitting space of current
        window.
        """
        self.add_mode = AddMode.VERTICAL | AddMode.SPLIT

    def cmd_size(self, x):
        """Change size of current window.

        (It's recommended to use `width()`/`height()` instead.)
        """
        self.focused_node.size = x
        self.refocus()

    def cmd_width(self, x):
        """Set width of current window."""
        self.focused_node.width = x
        self.refocus()

    def cmd_height(self, x):
        """Set height of current window."""
        self.focused_node.height = x
        self.refocus()

    def cmd_reset_size(self):
        """Reset size of current window to automatic (relative) sizing."""
        self.focused_node.reset_size()
        self.refocus()

    def cmd_grow(self, x):
        """Grow size of current window.

        (It's recommended to use `grow_width()`/`grow_height()` instead.)
        """
        self.focused_node.size += x
        self.refocus()

    def cmd_grow_width(self, x):
        """Grow width of current window."""
        self.focused_node.width += x
        self.refocus()

    def cmd_grow_height(self, x):
        """Grow height of current window."""
        self.focused_node.height += x
        self.refocus()
