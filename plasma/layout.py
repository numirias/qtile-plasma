import math
import logging
import copy

from libqtile.log_utils import logger
from libqtile.layout.base import Layout

from .node import Node, HORIZONTAL, VERTICAL


class Plasma(Layout):

    defaults = [
        # TODO Which options do we need?
        ('name', 'Plasma', 'Name of this layout.'),
        ('border_focus', '#ff0000', 'Border colour for the focused window.'),
        ('border_normal', '#000000', 'Border colour for un-focused winows.'),
        ('border_normal_fixed', '#b75500', ''),
        ('border_focus_fixed', '#ff7700', ''),
        ('border_width', 2, 'Border width.'),
        ('single_border_width', None, 'Border width for single window'),
        ('margin', 0, 'Margin of the layout.'),
    ]

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(Plasma.defaults)
        if self.single_border_width is None:
            self.single_border_width = self.border_width
        self.root = Node()
        self.split_orientation = None
        self.focused = None

    def _get_window(self):
        # TODO What's this for?
        return self.focused

    @property
    def focused_node(self):
        return self.root.find_payload(self.focused)

    def info(self):
        # TODO What's this for?
        return '(no info)'

    def focus(self, client):
        self.focused = client
        self.root.find_payload(client).access()

    def add(self, client):
        new_node = Node(client)
        if self.focused is None or self.focused_node is None:
            self.root.add_child(new_node)
        else:
            if self.split_orientation in (None, self.focused_node.parent.orient):
                self.focused_node.parent.add_child_after(new_node, self.focused_node)
            else:
                self.focused_node.split_with(new_node)
        self.split_orientation = None

    def remove(self, client):
        self.root.find_payload(client).remove()

    def clone(self, group):
        # TODO How to clone properly?
        c = copy.copy(self)
        c.group = group
        c.root = Node()
        c.root.parent = None
        c.focused = None
        return c

    def border_color(self, client):
        node = self.root.find_payload(client)
        if client is self.focused:
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
        logger.error('CONFIGURE %s %s' % (client, screen))
        self.root._x = screen.x
        self.root._y = screen.y
        self.root._width = screen.width
        self.root._height = screen.height

        node = self.root.find_payload(client)

        if len(self.root.children) == 1 and self.root.children[0].is_leaf:
            border_width = 0
        else:
            border_width = self.single_border_width

        logger.error('dimensions %s %s %s %s' % (node.x, node.y, node.width, node.height))

        client.place( # XXX Int conversions should happen in Node() not here
            int(node.x),
            int(node.y),
            int(node.width)-2,
            int(node.height)-2,
            border_width,
            self.border_color(client),
            margin=self.margin,
        )
        client.unhide()

    def focus_node(self, node):
        if node is None:
            return
        self.focused = node.payload
        self.group.focus(node.payload, False)

    def cmd_split_horizontal(self):
        self.split_orientation = HORIZONTAL

    def cmd_split_vertical(self):
        self.split_orientation = VERTICAL

    def cmd_grow(self, amt, orthogonal=False):
        orient = VERTICAL if orthogonal else HORIZONTAL
        self.focused_node.grow(amt, orient)
        self.group.focus(self.focused, False)

    def focus_first(self):
        pass

    def focus_last(self):
        pass

    def focus_next(self, window):
        pass

    def focus_previous(self, window):
        pass

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
        self.group.focus(self.focused, False)

    def cmd_move_right(self):
        self.focused_node.move_right()
        self.group.focus(self.focused, False)

    def cmd_move_up(self):
        self.focused_node.move_up()
        self.group.focus(self.focused, False)

    def cmd_move_down(self):
        self.focused_node.move_down()
        self.group.focus(self.focused, False)

    def cmd_integrate_left(self):
        self.focused_node.integrate(HORIZONTAL, -1)
        self.group.focus(self.focused, False)

    def cmd_integrate_right(self):
        self.focused_node.integrate(HORIZONTAL, 1)
        self.group.focus(self.focused, False)

    def cmd_integrate_up(self):
        self.focused_node.integrate(VERTICAL, -1)
        self.group.focus(self.focused, False)

    def cmd_integrate_down(self):
        self.focused_node.integrate(VERTICAL, 1)
        self.group.focus(self.focused, False)

    def cmd_reset_size(self):
        self.focused_node.reset_size()
        self.group.focus(self.focused, False)
