"""
    | teleorithm |

    need dict with id: widget, state, parts[by id]
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

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
                    height: 200
                    width: 300
                }
            }
        ''')
        style = dedent('''
            [Frame.Default.config]
        ''')
        self.toml_options = load_toml_string(style)
        tree = tkml_tree(source)
        self.root = TKMLVisitor().visit(tree)
        self.base = tkinter.Tk()

    def test_build_widget_returns_Widget(self):
        comp = rebuild(self.root)

        if t := self.toml_options.get(comp['type'], None):
            state, style = list(t.items())[0]
        
            props = {}
                
            for key in comp['props']:
                prop = style.get(key, {})
                prop.update(comp['props'][key])
                props[key] = prop
            comp['props'] = props

        widget = build_widget(comp, self.base)

        self.asrt(isinstance(widget, tkinter.Widget))
        # self.base.mainloop()


    def tearDown(self):
        with suppress(Exception):
            self.base.destroy()


class test_tkml_Frame_with_style_from_toml_string(Spec):
    def setUp(self):
        source = dedent('''
            Frame {}
        ''')
        tree = tkml_tree(source)

        style = dedent('''
            [Default.Frame]
            grid = { row = 0, column = 0, sticky = 'nsew' }
            grid_rowconfigure = { row = 0, weight = 1 }
            grid_columnconfigure = { col = 0, weight = 1 }

            [Default.Frame.config]
            bd = 2
            relief = 'solid'
            background= '#DD3344'
            width = 300
            height = 200
        ''')
        self.root = TKMLVisitor().visit(tree)
        self.toml_options = load_toml_string(style)
        self.base = tkinter.Tk()
        self.state = 'Default'

    def test_build_widget_returns_Widget(self):
        comp = rebuild(self.root)

        state_opts = self.toml_options[self.state]
        type_name, style = key_and_value(state_opts)
        
        def override_style_with_inline(style, inline):
            """
                style
                    : dict
                    : { method_name: kwargs_dict, ... }

                inline
                    : dict

                returns
                    > dict
            """
        props = {}
        for key in comp['props']:
            ordered_prop = style.get(key, {})
            ordered_prop.update(comp['props'][key])
            props[key] = ordered_prop
        style.update(props)


        override_style_with_inline(style, comp['props'])
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

    def test_build_widget_returns_Widget_with_inline_override(self):
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
        # self.base.mainloop()

    def tearDown(self):
        with suppress(Exception):
            self.base.destroy()


if __name__ == '__main__':
    main(testRunner=Runner)

