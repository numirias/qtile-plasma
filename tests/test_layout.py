from datetime import datetime
from pathlib import Path
from pytest import fixture, mark
import sys

from plasma import Plasma
from plasma.node import Node

# We borrow Qtile's testing framework. That's not elegant but the best option.
sys.path.insert(0, str(Path(__file__).parents[1] / 'lib'))  # noqa: E402
from qtile.libqtile import config
from qtile.libqtile.layout.floating import Floating
from qtile.test.conftest import no_xinerama, qtile, xephyr, xvfb  # noqa: F401
from qtile.test.layouts.layout_utils import assertFocused


@fixture
def grid(qtile):
    qtile.testWindow('a')
    qtile.testWindow('b')
    qtile.c.layout.previous()
    qtile.c.layout.split_vertical()
    qtile.testWindow('c')
    qtile.c.layout.right()
    qtile.c.layout.split_vertical()
    qtile.testWindow('d')

class Config:

    auto_fullscreen = True
    main = None
    groups = [
        config.Group('g0'),
        config.Group('g1'),
        config.Group('g2'),
        config.Group('g3')
    ]
    layouts = [Plasma()]
    floating_layout = Floating()
    keys = []
    mouse = []
    screens = []
    follow_mouse_focus = False

def plasma_config(func):
    config = mark.parametrize('qtile', [Config], indirect=True)(func)
    return no_xinerama(config)

def tree(qtile):
    return qtile.c.layout.info()['tree']

class TestLayout:

    def test_init(self):
        layout = Plasma()
        assert isinstance(layout.root, Node)

    def test_focus(self, root):
        layout = Plasma()
        layout.root = root
        a, b, c, d = 'abcd'
        layout.add(a)
        layout.add(b)
        layout.add(c)
        layout.add(d)
        assert layout.focus_first() == 'a'
        assert layout.focus_last() == 'd'
        assert layout.focus_next('b') == 'c'
        assert layout.focus_previous('c') == 'b'
        layout.focus('c')
        assert layout.focused is c

    def test_access(self, root):
        layout = Plasma()
        layout.root = root
        layout.add('a')
        now = datetime.now()
        assert layout.root.find_payload('a').last_accessed < now
        layout.focus('a')
        assert layout.root.find_payload('a').last_accessed > now

    @plasma_config
    def test_info(self, qtile):
        qtile.testWindow('a')
        qtile.testWindow('b')
        assert qtile.c.layout.info()['tree'] == ['a', 'b']

    @plasma_config
    def test_windows(self, qtile):
        qtile.testWindow('a')
        qtile.testWindow('b')
        qtile.testWindow('c')
        assertFocused(qtile, 'c')
        assert tree(qtile) == ['a', 'b', 'c']

    @plasma_config
    def test_split_directions(self, qtile):
        qtile.testWindow('a')
        qtile.c.layout.split_horizontal()
        qtile.testWindow('b')
        qtile.c.layout.split_vertical()
        qtile.testWindow('c')
        assert tree(qtile) == ['a', ['b', 'c']]

    @plasma_config
    def test_directions(self, qtile, grid):
        assertFocused(qtile, 'd')
        qtile.c.layout.left()
        assertFocused(qtile, 'c')
        qtile.c.layout.up()
        assertFocused(qtile, 'a')
        qtile.c.layout.right()
        assertFocused(qtile, 'b')
        qtile.c.layout.down()
        assertFocused(qtile, 'd')
        qtile.c.layout.down()
        assertFocused(qtile, 'd')
        qtile.c.layout.previous()
        assertFocused(qtile, 'b')
        qtile.c.layout.next()
        assertFocused(qtile, 'd')

    @plasma_config
    def test_move(self, qtile, grid):
        assert tree(qtile) == [['a', 'c'], ['b', 'd']]
        qtile.c.layout.move_up()
        assert tree(qtile) == [['a', 'c'], ['d', 'b']]
        qtile.c.layout.move_down()
        assert tree(qtile) == [['a', 'c'], ['b', 'd']]
        qtile.c.layout.move_left()
        assert tree(qtile) == [['a', 'c'], 'd', 'b']
        qtile.c.layout.move_right()
        assert tree(qtile) == [['a', 'c'], 'b', 'd']

    @plasma_config
    def test_integrate(self, qtile, grid):
        qtile.c.layout.integrate_left()
        assert tree(qtile) == [['a', 'c', 'd'], 'b']
        qtile.c.layout.integrate_up()
        assert tree(qtile) == [['a', ['c', 'd']], 'b']
        qtile.c.layout.integrate_up()
        qtile.c.layout.integrate_down()
        assert tree(qtile) == [['a', ['c', 'd']], 'b']
        qtile.c.layout.integrate_right()
        assert tree(qtile) == [['a', 'c'], ['b', 'd']]

    @plasma_config
    def test_sizes(self, qtile):
        qtile.testWindow('a')
        qtile.testWindow('b')
        qtile.c.layout.split_vertical()
        qtile.testWindow('c')
        info = qtile.c.window.info()
        assert info['x'] == 400
        assert info['y'] == 300
        assert info['width'] == 398
        assert info['height'] == 298
        qtile.c.layout.grow_height(50)
        info = qtile.c.window.info()
        assert info['height'] == 298 + 50
        qtile.c.layout.grow_width(50)
        info = qtile.c.window.info()
        assert info['width'] == 398 + 50
        qtile.c.layout.reset_size()
        info = qtile.c.window.info()
        assert info['height'] == 298
        qtile.c.layout.height(300)
        info = qtile.c.window.info()
        assert info['height'] == 300 - 2
        qtile.c.layout.width(250)
        info = qtile.c.window.info()
        assert info['width'] == 250 - 2
        qtile.c.layout.size(200)
        info = qtile.c.window.info()
        assert info['height'] == 200 - 2
        qtile.c.layout.grow(10)
        info = qtile.c.window.info()
        assert info['height'] == 210 - 2

    @plasma_config
    def test_remove(self, qtile):
        a = qtile.testWindow('a')
        b = qtile.testWindow('b')
        assert tree(qtile) == ['a', 'b']
        qtile.kill_window(a)
        assert tree(qtile) == ['b']
        qtile.kill_window(b)
        assert tree(qtile) == []
