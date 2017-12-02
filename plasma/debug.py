from collections import defaultdict


class Canvas:

    horizontal_line = '\u2500'
    vertical_line = '\u2502'
    tl_corner = '\u250c'
    tr_corner = '\u2510'
    bl_corner = '\u2514'
    br_corner = '\u2518'

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.canvas = defaultdict(lambda: defaultdict(lambda: '#'))

    def add_box(self, x, y, width, height, name='*'):
        width = width-1
        height = height-1
        label = str(name)[:width-1]
        for i in range(x, width+x):
            self.canvas[i][y] = self.horizontal_line
            self.canvas[i][y+height] = self.horizontal_line
        for i in range(y, height+y):
            self.canvas[x][i] = self.vertical_line
            self.canvas[x+width][i] = self.vertical_line
        for i in range(x+1, width+x):
            for j in range(y+1, y+height):
                self.canvas[i][j] = '.'
        for i in range(len(label)):
            self.canvas[x+1+i][y+1] = label[i]
        self.canvas[x][y] = self.tl_corner
        self.canvas[x+width][y] = self.tr_corner
        self.canvas[x][y+height] = self.bl_corner
        self.canvas[x+width][y+height] = self.br_corner

    def view(self):
        res = ''
        for y in range(self.height):
            for x in range(self.width):
                res += self.canvas[x][y]
            res += '\n'
        return res

def tree(node, level=0):
    res = '{indent}{name} {orient} {repr_} {pos} {size} {parent}\n'.format(
        indent=level*4*' ',
        name='%s' % (node.payload or '*'),
        orient='H' if node.horizontal else 'V',
        repr_='%s' % repr(node),
        pos='%g*%g@%g:%g' % (node.width, node.height, node.x, node.y),
        size='size: %s%s' % (node.size, ' (auto)' if node.flexible else ''),
        parent='p: %s' % node.parent,
    )
    for child in node.children:
        res += tree(child, level+1)
    return res

def draw(root):
    canvas = Canvas(root.width, root.height)
    def add(node):
        if node.is_leaf:
            canvas.add_box(
                *node.pixel_perfect,
                node.payload
            )
        for child in node.children:
            add(child)
    add(root)
    return canvas.view()

def info(node):
    print(tree(node))
    print(draw(node))
