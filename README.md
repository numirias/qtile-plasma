# Plasma

[![PyPI Version](https://img.shields.io/pypi/v/qtile-plasma.svg)](https://pypi.python.org/pypi/qtile-plasma)
[![Python Versions](https://img.shields.io/pypi/pyversions/qtile-plasma.svg)](https://pypi.python.org/pypi/qtile-plasma)
[![Build Status](https://travis-ci.org/numirias/qtile-plasma.svg?branch=master)](https://travis-ci.org/numirias/qtile-plasma)
[![codecov](https://codecov.io/gh/numirias/qtile-plasma/branch/master/graph/badge.svg)](https://codecov.io/gh/numirias/qtile-plasma)

Plasma is an advanced, flexible layout for [Qtile](https://github.com/qtile/qtile/).

If you're looking for a well-tested and maintained alternative to Qtile's default layouts, give it a try.

## About

Plasma works on a tree structure. Each tree node represents a container whose children are aligned either horizontally or vertically (similar to [i3](https://i3wm.org/)). Each window is attached to a leaf of the tree and takes either a calculated relative amount or a custom absolute amount of space in its parent container. Windows can be resized, rearranged and seamlessly integrated into other containers, enabling lots of different setups.

## Installation

Install the package, e.g. via pip:

```
pip install qtile-plasma
```
    
Add the layout to your config (`~/.config/qtile/config.py`):

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
    'M-d': lazy.layout.split_horizontal(),
    'M-v': lazy.layout.split_vertical(),
    'M-a': lazy.layout.grow_width(30),
    'M-x': lazy.layout.grow_width(-30),
    'M-S-a': lazy.layout.grow_height(30),
    'M-S-x': lazy.layout.grow_height(-30),
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
    <td><code>split_horizontal()</code></td>
    <td>Add next window horizontally.</td>
  </tr>
  <tr>
    <td><code>split_vertical()</code></td>
    <td>Add next window vertically.</td>
  </tr>
  <tr>
    <td><code>size(val)</code></td>
    <td>Change size of current window.

(It's recommended to use `width()`/`height()` instead.)</td>
  </tr>
  <tr>
    <td><code>width(val)</code></td>
    <td>Set width of current window.</td>
  </tr>
  <tr>
    <td><code>height(val)</code></td>
    <td>Set height of current window.</td>
  </tr>
  <tr>
    <td><code>reset_size()</code></td>
    <td>Reset size of current window to automatic (relative) sizing.</td>
  </tr>
  <tr>
    <td><code>grow(amt)</code></td>
    <td>Grow size of current window.

(It's recommended to use `grow_width()`/`grow_height()` instead.)</td>
  </tr>
  <tr>
    <td><code>grow_width(amt)</code></td>
    <td>Grow width of current window.</td>
  </tr>
  <tr>
    <td><code>grow_height(amt)</code></td>
    <td>Grow height of current window.</td>
  </tr>
</table>
<!--commands-end-->

---

If you have found a bug or want to suggest a feature, please [file an issue](https://github.com/numirias/qtile-plasma/issues/new).
