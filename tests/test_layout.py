from pytest import fixture

from plasma import Plasma
from plasma.node import Node


@fixture
def layout():
    layout = Plasma()
    return layout

class TestLayout:

    def test_init(self):
        layout = Plasma()
        assert type(layout.root) == Node

    def test_add(self, layout):
        layout.add('x')
        assert layout.root.tree == [layout.root.find_payload('x')]

    def test_focus(self, layout):
        pass
        # TODO
    # TODO More tests
