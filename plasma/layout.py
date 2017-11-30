import math
import logging
import copy

from libqtile.log_utils import logger
from libqtile.layout.base import Layout
from .node import Node, HORIZONTAL, VERTICAL


class Plasma(Layout):

    defaults = [
        ('name', 'Plasma', 'Layout name'),
        ('border_normal', '#000000', 'Unfocused window border color'),
        ('border_focus', '#ff0000', 'Focused window border color'),
        ('border_normal_fixed', '#111111', 'Unfocused fixed-size window border color'),
        ('border_focus_fixed', '#ee0000', 'Focused fixed-size window border color'),
        ('border_width', 2, 'Border width'),
        ('single_border_width', None, 'Single window border width'),
        ('margin', 0, 'Layout margin'),
    ]

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(Plasma.defaults)
        if self.single_border_width is None:
            self.single_border_width = self.border_width
        self.root = Node()
        self.focused = None
        self.split_orientation = None

    @property
    def focused_node(self):
        return self.root.find_payload(self.focused)

    def focus(self, client):
        self.focused = client
        self.root.find_payload(client).access()

    def add(self, client):
        node = Node(client)
        if self.focused is None or self.focused_node is None:
            self.root.add_child(node)
            return
        if self.split_orientation in (None, self.focused_node.parent.orient):
            self.focused_node.parent.add_child_after(node, self.focused_node)
        else:
            self.focused_node.split_with(node)
        self.split_orientation = None

    def remove(self, client):
        self.root.find_payload(client).remove()

    def clone(self, group):
        logger.error('CLONE')
        # TODO How to clone properly?
        c = copy.copy(self)
        c.group = group
        c.root = Node()
        c.root.parent = None
        c.focused = None
        return c

    def border_color(self, client):
        node = self.root.find_payload(client)
        if client.has_focus:
            if node.flexible:
                color = self.border_focus
            else:
                color = self.border_focus_fixed
        else:
            if node.flexible:
                color = self.border_normal
            else:
                color = self.border_normal_fixed
        color_pixel = self.group.qtile.colorPixel(color)
        return color_pixel

    def configure(self, client, screen):
        self.root._x = screen.x
        self.root._y = screen.y
        self.root._width = screen.width
        self.root._height = screen.height
        node = self.root.find_payload(client)
        logger.error('CONFIGURE %s %s (%s:%s %s*%s' % \
                     (client, screen, node.x, node.y, node.width, node.height))
        if len(self.root.children) == 1 and self.root.children[0].is_leaf:
            border_width = 0
        else:
            border_width = self.single_border_width
         # TODO Convert to int inside Node, not here
        client.place(
            int(node.x),
            int(node.y),
            int(node.width)-2,
            int(node.height)-2,
            border_width,
            self.border_color(client),
            margin=self.margin,
        )
        client.unhide()

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
        self.group.focus(node.payload)

    def refocus(self):
        self.group.focus(self.focused)

    def cmd_next(self):
        node = self.focused_node.prev_leaf
        self.focus_node(node)

    def cmd_previous(self):
        node = self.focused_node.next_leaf
        self.focus_node(node)

    def cmd_left(self):
        node = self.focused_node.left
        self.focus_node(node)

    def cmd_right(self):
        node = self.focused_node.right
        self.focus_node(node)

    def cmd_up(self):
        node = self.focused_node.up
        self.focus_node(node)

    def cmd_down(self):
        node = self.focused_node.down
        self.focus_node(node)

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
        self.split_orientation = HORIZONTAL

    def cmd_split_vertical(self):
        self.split_orientation = VERTICAL

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
