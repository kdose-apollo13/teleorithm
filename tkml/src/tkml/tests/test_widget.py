"""
    | teleorithm |
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from copy import deepcopy
from contextlib import suppress
from textwrap import dedent
import tkinter

from tkml.grammar import tkml_tree
from tkml.tkmlvisitor import TKMLVisitor
from tkml.component import rebuild
from tkml.widget import build_widget
from tkml import wrapped_methods
from tkml.utils import load_toml_string, key_and_value


class test_tkml_Frame_with_style_defined_inline(Spec):
    def setUp(self):
        source = dedent('''
            Frame {
                grid { row: 0 column: 0 sticky: 'nsew' }
                grid_rowconfigure { row: 0 weight: 1 }
                grid_columnconfigure { col: 0 weight: 1 }
                config {
                    relief: 'solid'
                    background: '#DD3344'
                    width: 300
                    height: 200
                }
            }
        ''')
        tree = tkml_tree(source)
        root = TKMLVisitor().visit(tree)
        self.comp = rebuild(root)
        self.base = tkinter.Tk()

    def test_build_widget_returns_Widget(self):
        widget = build_widget(self.comp, self.base)
        self.asrt(isinstance(widget, tkinter.Widget))
        # self.base.mainloop()

    def tearDown(self):
        with suppress(Exception):
            self.base.destroy()


class test_tkml_Frame_with_style_from_toml_string(Spec):
    def setUp(self):
        source = dedent('''
            Frame {
                grid { row: 0 column: 0 sticky: 'nsew' }
            }
        ''')
        tree = tkml_tree(source)

        style = dedent('''
            [Frame]
            grid = { row = 0, column = 0, sticky = 'nsew' }
            grid_rowconfigure = { row = 0, weight = 1 }
            grid_columnconfigure = { col = 0, weight = 1 }

            [Frame.config]
            bd = 2
            relief = 'solid'
            background= '#DD3344'
            width = 300
            height = 200
        ''')
        self.root = TKMLVisitor().visit(tree)
        self.toml_options = load_toml_string(style)
        self.base = tkinter.Tk()

    def test_build_widget_returns_Widget(self):
        comp = rebuild(self.root)

        type_name = comp['type']
        style = self.toml_options[type_name]
        # override inline style
        comp['props'].update(style)
        widget = build_widget(comp, self.base)

        self.asrt(isinstance(widget, tkinter.Widget))
        # self.base.mainloop()

    def tearDown(self):
        with suppress(Exception):
            self.base.destroy()


class test_tkml_Frame_with_state_style_from_toml_string(Spec):
    def setUp(self):
        source = dedent('''
            Frame {
                config { background: #22DDEE height: 400 }
            }
        ''')
        tree = tkml_tree(source)

        style = dedent('''
            [Frame.default]
            grid = { row = 0, column = 0, sticky = 'nsew' }
            grid_rowconfigure = { row = 0, weight = 1 }
            grid_columnconfigure = { col = 0, weight = 1 }

            [Frame.default.config]
            bd = 2
            relief = 'solid'
            background= '#DD3344'
            width = 400
            height = 200
        ''')
        self.root = TKMLVisitor().visit(tree)
        self.toml_options = load_toml_string(style)
        self.base = tkinter.Tk()

    def test_build_widget_returns_Widget(self):
        comp = rebuild(self.root)

        type_name = comp['type']
        state, style = list(self.toml_options[type_name].items())[0]

        # inline style overrides file style
        props = {}
        for key in comp['props']:
            ordered_prop = style.get(key, {})
            ordered_prop.update(comp['props'][key])
            props[key] = ordered_prop
        style.update(props)
        comp['props'] = style

        widget = build_widget(comp, self.base)

        self.asrt(isinstance(widget, tkinter.Widget))
        self.base.mainloop()

    def tearDown(self):
        with suppress(Exception):
            self.base.destroy()


if __name__ == '__main__':
    main(testRunner=Runner)

