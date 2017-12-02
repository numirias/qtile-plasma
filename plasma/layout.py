import math
import logging
import copy

from xcffib.xproto import StackMode
from libqtile.log_utils import logger
from libqtile.layout.base import Layout

from .node import Node, HORIZONTAL, VERTICAL


class Plasma(Layout):

    defaults = [
        ('name', 'Plasma', 'Layout name'),
        ('border_normal', '#333333', 'Unfocused window border color'),
        ('border_focus', '#00e891', 'Focused window border color'),
        ('border_normal_fixed', '#333333', 'Unfocused fixed-size window border color'),
        ('border_focus_fixed', '#00e8dc', 'Focused fixed-size window border color'),
        ('border_width', 1, 'Border width'),
        ('border_width_single', 0, 'Border width for single window'),
        ('margin', 0, 'Layout margin'),
    ]

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(Plasma.defaults)
        self.root = Node()
        self.focused = None
        self.split_orient = None

    def clone(self, group):
        clone = copy.copy(self)
        clone.group = group
        clone.root = Node()
        clone.focused = None
        clone.split_orient = None
        return clone

    def add(self, client):
        node = Node(client)
        if self.focused is None or self.focused_node is None:
            self.root.add_child(node)
            return
        if self.split_orient in (None, self.focused_node.parent.orient):
            self.focused_node.parent.add_child_after(node, self.focused_node)
        else:
            self.focused_node.split_with(node)
        self.split_orient = None

    def remove(self, client):
        self.root.find_payload(client).remove()

    def configure(self, client, screen):
        self.root._x = screen.x
        self.root._y = screen.y
        self.root._width = screen.width
        self.root._height = screen.height
        node = self.root.find_payload(client)
        border_width = \
            self.border_width_single if self.root.tree == [node] else \
            self.border_width
        border_color = getattr(self, 'border_' + \
            ('focus' if client.has_focus else 'normal') + \
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

    @property
    def focused_node(self):
        return self.root.find_payload(self.focused)

    def refocus(self):
        self.group.focus(self.focused)

    def cmd_next(self):
        self.focus_node(self.focused_node.prev_leaf)

    def cmd_previous(self):
        self.focus_node(self.focused_node.next_leaf)

    def cmd_left(self):
        self.focus_node(self.focused_node.left)

    def cmd_right(self):
        self.focus_node(self.focused_node.right)

    def cmd_up(self):
        self.focus_node(self.focused_node.up)

    def cmd_down(self):
        self.focus_node(self.focused_node.down)

    def cmd_move_left(self):
        self.focused_node.move_left()
        self.refocus()

    def cmd_move_right(self):
        self.focused_node.move_right()
        self.refocus()

    def cmd_move_up(self):
        self.focused_node.move_up()
        self.refocus()

    def cmd_move_down(self):
        self.focused_node.move_down()
        self.refocus()

    def cmd_integrate_left(self):
        self.focused_node.integrate_left()
        self.refocus()

    def cmd_integrate_right(self):
        self.focused_node.integrate_right()
        self.refocus()

    def cmd_integrate_up(self):
        self.focused_node.integrate_up()
        self.refocus()

    def cmd_integrate_down(self):
        self.focused_node.integrate_down()
        self.refocus()

    def cmd_split_horizontal(self):
        self.split_orient = HORIZONTAL

    def cmd_split_vertical(self):
        self.split_orient = VERTICAL

    def cmd_size(self, size):
        self.focused_node.size = size
        self.refocus()

    def cmd_reset_size(self):
        self.focused_node.reset_size()
        self.refocus()

    def cmd_grow(self, amt, orthogonal=False):
        orient = VERTICAL if orthogonal else HORIZONTAL
        self.focused_node.grow(amt, orient)
        self.refocus()
