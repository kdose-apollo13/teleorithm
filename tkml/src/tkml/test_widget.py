"""
    | teleorithm |
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from textwrap import dedent
import tkinter

from tkml.grammar import tkml_tree
from tkml.tkmlvisitor import TKMLVisitor
from tkml.component import rebuild

import wrapped_methods


class test_root_component_of_simple_Frame(Spec):
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

    def test_build_widget(self):
        def build_widget(comp, base):
            """
                comp
                    : dict
                    : {
                        'type': '',
                        'script_props': { method_name: option_dict },
                        'style_props': { method_name: option_dict },
                        parts: []
                      }

                base
                    : tkinter.Widget

                returns
                    > tkinter.Widget
            """
            type_name = comp['type']
            tk_class = getattr(tkinter, type_name)
            widget = tk_class(base)
            options = {**comp['script_props'], **comp['style_props']}
            for name, opt in options.items():
                func = getattr(wrapped_methods, name, None)
                func(widget, opt)

            for part in comp['parts']:
                return build_widget(part, widget)

            return widget

        w = build_widget(self.comp, self.base)
        self.base.mainloop()




if __name__ == '__main__':
    main(testRunner=Runner)

