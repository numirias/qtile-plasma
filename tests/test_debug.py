from plasma.debug import draw, tree, info


class TestDebugging:

    def test_tree(self, root, grid):
        lines = tree(root).split('\n')
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
