# Plasma

[![Build Status](https://travis-ci.org/numirias/qtile-plasma.svg?branch=master)](https://travis-ci.org/numirias/qtile-plasma)
[![codecov](https://codecov.io/gh/numirias/qtile-plasma/branch/master/graph/badge.svg)](https://codecov.io/gh/numirias/qtile-plasma)
[![PyPI Version](https://img.shields.io/pypi/v/qtile-plasma.svg)](https://pypi.python.org/pypi/qtile-plasma)
[![Python Versions](https://img.shields.io/pypi/pyversions/qtile-plasma.svg)](https://pypi.python.org/pypi/qtile-plasma)

Plasma is a flexible, tree-based layout for [Qtile](https://github.com/qtile/qtile/).

If you're looking for a well-tested and maintained alternative to Qtile's default layouts, give it a try.

## About

Plasma works on a tree structure. Each node represents a container with child containers aligned either horizontally or vertically (similar to [i3](https://i3wm.org/)). Each window is attached to a leaf, taking either a proportional or a specific custom amount of space in its parent container. Windows can be resized, rearranged and integrated into other containers, enabling lots of different setups.

## Demo

Here is a quick demo showing some of the main features (adding modes, moving, integrating and resizing):

![Demo](https://i.imgur.com/N3CMonP.gif)

## Installation

Install the package. You can [get it from PyPI](https://pypi.python.org/pypi/qtile-plasma/):

```
pip install --upgrade qtile-plasma
```

Or, if you're running Arch Linux, you can also [get it from AUR](https://aur.archlinux.org/packages/qtile-plasma/):

```
pacaur -S qtile-plasma
```
    
Then, add the layout to your config (`~/.config/qtile/config.py`):

```python
from plasma import Plasma
...
layouts = [
    Plasma(
        border_normal='#333333',
        border_focus='#00e891',
        border_normal_fixed='#006863',
        border_focus_fixed='#00e8dc',
        border_width=1,
        border_width_single=0,
        margin=0
    ),
    ...
]
```

Add some key bindings, too. I am using these:

```python
from libqtile.command import lazy
from libqtile.config import EzKey
...
keymap = {
    'M-h': lazy.layout.left(),
    'M-j': lazy.layout.down(),
    'M-k': lazy.layout.up(),
    'M-l': lazy.layout.right(),
    'M-S-h': lazy.layout.move_left(),
    'M-S-j': lazy.layout.move_down(),
    'M-S-k': lazy.layout.move_up(),
    'M-S-l': lazy.layout.move_right(),
    'M-A-h': lazy.layout.integrate_left(),
    'M-A-j': lazy.layout.integrate_down(),
    'M-A-k': lazy.layout.integrate_up(),
    'M-A-l': lazy.layout.integrate_right(),
    'M-d': lazy.layout.mode_horizontal(),
    'M-v': lazy.layout.mode_vertical(),
    'M-S-d': lazy.layout.mode_horizontal_split(),
    'M-S-v': lazy.layout.mode_vertical_split(),
    'M-a': lazy.layout.grow_width(30),
    'M-x': lazy.layout.grow_width(-30),
    'M-S-a': lazy.layout.grow_height(30),
    'M-S-x': lazy.layout.grow_height(-30),
    'M-C-5': lazy.layout.size(500),
    'M-C-8': lazy.layout.size(800),
    'M-n': lazy.layout.reset_size(),
}
keys = [EzKey(k, v) for k, v in keymap.items()]
```

Done!

## Commands

The layout exposes the following commands:

<!--commands-start-->
<table>
  <tr>
    <td><code>next()</code></td>
    <td>Focus next window.</td>
  </tr>
  <tr>
    <td><code>previous()</code></td>
    <td>Focus previous window.</td>
  </tr>
  <tr>
    <td><code>recent()</code></td>
    <td>Focus most recently focused window.<br>
(Toggles between the two latest active windows.)</td>
  </tr>
  <tr>
    <td><code>left()</code></td>
    <td>Focus window to the left.</td>
  </tr>
  <tr>
    <td><code>right()</code></td>
    <td>Focus window to the right.</td>
  </tr>
  <tr>
    <td><code>up()</code></td>
    <td>Focus window above.</td>
  </tr>
  <tr>
    <td><code>down()</code></td>
    <td>Focus window below.</td>
  </tr>
  <tr>
    <td><code>move_left()</code></td>
    <td>Move current window left.</td>
  </tr>
  <tr>
    <td><code>move_right()</code></td>
    <td>Move current window right.</td>
  </tr>
  <tr>
    <td><code>move_up()</code></td>
    <td>Move current window up.</td>
  </tr>
  <tr>
    <td><code>move_down()</code></td>
    <td>Move current window down.</td>
  </tr>
  <tr>
    <td><code>integrate_left()</code></td>
    <td>Integrate current window left.</td>
  </tr>
  <tr>
    <td><code>integrate_right()</code></td>
    <td>Integrate current window right.</td>
  </tr>
  <tr>
    <td><code>integrate_up()</code></td>
    <td>Integrate current window up.</td>
  </tr>
  <tr>
    <td><code>integrate_down()</code></td>
    <td>Integrate current window down.</td>
  </tr>
  <tr>
    <td><code>mode_horizontal()</code></td>
    <td>Next window will be added horizontally.</td>
  </tr>
  <tr>
    <td><code>mode_vertical()</code></td>
    <td>Next window will be added vertically.</td>
  </tr>
  <tr>
    <td><code>mode_horizontal_split()</code></td>
    <td>Next window will be added horizontally, splitting space of current
window.</td>
  </tr>
  <tr>
    <td><code>mode_vertical_split()</code></td>
    <td>Next window will be added vertically, splitting space of current
window.</td>
  </tr>
  <tr>
    <td><code>size(x)</code></td>
    <td>Change size of current window.<br>
(It's recommended to use <code>width()</code>/<code>height()</code> instead.)</td>
  </tr>
  <tr>
    <td><code>width(x)</code></td>
    <td>Set width of current window.</td>
  </tr>
  <tr>
    <td><code>height(x)</code></td>
    <td>Set height of current window.</td>
  </tr>
  <tr>
    <td><code>reset_size()</code></td>
    <td>Reset size of current window to automatic (relative) sizing.</td>
  </tr>
  <tr>
    <td><code>grow(x)</code></td>
    <td>Grow size of current window.<br>
(It's recommended to use <code>grow_width()</code>/<code>grow_height()</code> instead.)</td>
  </tr>
  <tr>
    <td><code>grow_width(x)</code></td>
    <td>Grow width of current window.</td>
  </tr>
  <tr>
    <td><code>grow_height(x)</code></td>
    <td>Grow height of current window.</td>
  </tr>
</table>
<!--commands-end-->

## Contributing

If you have found a bug or want to suggest a feature, please [file an issue](https://github.com/numirias/qtile-plasma/issues/new).


To work on Plasma locally, you need to clone submodules too, since the layout integration tests use some of Qtile's test fixtures:

```
git clone --recursive https://github.com/numirias/qtile-plasma/
```

Also make sure you meet the [hacking requirements of Qtile](http://docs.qtile.org/en/latest/manual/hacking.html). In particular, have `xserver-xephyr` installed. Then run:

```
make init
```

If that fails, run the `init` instructions from the [Makefile](https://github.com/numirias/qtile-plasma/blob/master/Makefile) one by one.

All new changes need to be fully test-covered and pass the linting:

```
make lint
make test
```

If you made changes to the layout API, also re-build this README's [commands](#commands) section:

```
make readme
```
