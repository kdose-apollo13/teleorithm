"""
TODO:
- draw cool borders, picture frames etc... around leaves
- dramatic lighting, spotlight effect for text (hyperbola + gradient?)

"""
import json
from tkinter import *
from tkinter.font import nametofont

import monkeypatch  # fukyah

from leaf3 import Leaf
from syneng import the_mighty_canonical_spans as text_to_tagspans


with open('syncolor.json', 'rt') as r:
    # TODO: convert to configparser -> sections Numbers etc...
    colors = json.load(r)
    # if you want to change user-facing names do it here
    tag_colors = {
        "string": colors["string"],
        "string3": colors["string3"],
        "comment": colors["comment"],
        "method": colors["method"],
        "function": colors["function"],
        "decorator": colors["decorator"],
        "kw_param": colors["kw_param"],
        "keyword": colors["keyword"],
        "builtin": colors["builtin"],
        "point_float": colors["point_float"],
        "exponent_float": colors["exponent_float"],
        "imaginary": colors["imaginary"],
        "bin_integer": colors["bin_integer"],
        "oct_integer": colors["oct_integer"],
        "hex_integer": colors["hex_integer"],
        "dec_integer": colors["dec_integer"],
        "dec_zero": colors["dec_zero"],
        "todo": colors["todo"]
    }


class App(Tk):
    """
        this is pretty wild - just draw a canvas
        all over whatever the root window opens
        figure out what stuff is visible
        and then draw it whenever

        it's up to this to define hilight behavior
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # _tkinter.tkapp

        # PLACE THE WINDOW
        w_screen = self.winfo_screenwidth()
        h_screen = self.winfo_screenheight()
        # some reasonable whatever
        w, h, x, y = 860, 1010, 0, 0
        default_geometry = '{}x{}+{}+{}'.format(w, h, x, y)
        self.geometry(default_geometry)

        self.width, self.height, self.x, self.y = w, h, x, y
        
        # BLAST A CANVAS
        c = Canvas(self, width=self.width, height=self.height)
        default_c = {
            'highlightthickness': 0,  # no box around leaves
        }
        c.config(default_c)
        c.grid(row=0, column=0, sticky=(N, S, E, W))  # sticky? manually?
        self.canvas = c
        
        l = Leaf(c)  # from leaf info interface
        l.set_syntax(tag_colors, text_to_tagspans)

        self.Z = 2  # TODO: buh?
        c.create_window(self.Z, self.Z, anchor='nw', window=l)

        # where are these coming from? some interface that gives leaf info
        self.leaves = []
        self.leaves.append(l)

        # self.after(1000, lambda: l.set_hili_color('#FF0000'))
        # self.after(2000, lambda: self._reset_leaf(l))
        
        self.update_idletasks()  # update display, don't process user events
        self._manage_geometry()
        
        self.bind('<Configure>', self._on_configure)

        def safe_close():
            # do stuff here if necessary
            self.destroy()

        self.protocol('WM_DELETE_WINDOW', safe_close)

        self.focus()

    def _highlight_leaf(self, l):
        """
            l: Leaf
        """
        # TODO: where is this color coming from?
        l.set_hili_color('#22CCCC')

    def _reset_leaf(self, l):
        """
            l: Leaf
        """
        l.set_hili_color('#333333')


    def _on_configure(self, e):
        self._manage_geometry()

    def _manage_geometry(self):
        w = self.winfo_width()
        h = self.winfo_height()
        
        self.canvas.config(width=w, height=h)
        
        for leaf in self.leaves:
            # what dimension can leaf acquire?
            oo = 2 * self.Z
            leaf.redraw(w - oo, h - oo)


if __name__ == '__main__':
    app = App()
    app.mainloop()

# TODO: some kind of debounce for resize?

