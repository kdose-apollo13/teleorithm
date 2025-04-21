"""
    | teleorithm |

    TDD
    the time pincer comes together
    test_wisp8 happens first
    functions migrate out to wisp8
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from textwrap import dedent
import tomllib

from tkml.grammar import tkml_tree
from tkml.component import comb_for_components, TKMLFilter

from tkinter import *


def loads_toml(string):
    d = tomllib.loads(string)
    return d


def load_toml(path):
    with open(path, 'rb') as r:
        d = tomllib.load(r)
    return d


class Test_Scrollable_when(Spec):
    def setUp(self):
        source = dedent('''
            Scrollable { }
        ''')
        tree = tkml_tree(source)
        self.specs = comb_for_components(tree, TKMLFilter())
        self.style = loads_toml(dedent('''
            [Scrollable]
        '''))
    
    # // OBSERVE //
    def test_returns_something(self):
        self.equa(
            self.specs,
            {'type': 'Scrollable', 'props': {}, 'parts': []}
        )

        self.equa(
            self.style,
            {'Scrollable': {}}
        )
        # WHAT NOW?
        # JUST MAKE SOME FUNCTION THAT DOES SOMETHING WITH THESE THINGS

    # // OBSERVE //

# TARGET
source = dedent('''
    Scrollable {
        Frame {
            id: container

            Canvas {
                id: viewport
                config: yscrollcommand: scrollbar.set

                Frame { 
                    id: content 
                }
            }

            Scrollbar { 
                id: scrollbar
                config: command: viewport.yview
            }
        }
    }
''')


if __name__ == '__main__':
    main(testRunner=Runner)

