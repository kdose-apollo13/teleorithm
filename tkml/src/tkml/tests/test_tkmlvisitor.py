"""
    | teleorithm |
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from parsimonious.nodes import Node
from parsimonious.grammar import Grammar

from textwrap import dedent
from tkinter import *

from tkml.grammar import tkml_tree
from tkml.tkmlvisitor import walk_tree_for_components, TKMLVisitor

from tkml.utils import count_nodes


class test_curly_braces_within_an_f_string(Spec):
    def setUp(self):
        self.thing = 'whatever'
    
    def test_are_preserved_by_doubling_the_brace_chars(self):
        s = f'outer braces {{ all the {self.thing} forever and ever }}'
        self.equa(
            s,
            'outer braces { all the whatever forever and ever }'
        )

class test_single_and_multiline_sources(Spec):
    def setUp(self):
        self.single = 'Name {}'

        self.multi = dedent('''\
        Name {}''')

    def test_represent_same_value(self):
        self.equa(self.single, self.multi)

    def test_have_identical_trees(self):
        tree_single = tkml_tree(self.single)
        tree_multi = tkml_tree(self.multi)
        self.equa(tree_single, tree_multi)
        
class test_trivial_tkml_tree_when_walked_for_components(Spec):
    def setUp(self):
        source = 'Name {}'
        self.tree = tkml_tree(source)
        self.walker = TKMLVisitor()

    def test_returns_dict(self):
        comps = walk_tree_for_components(self.tree, self.walker)
        self.asrt(isinstance(comps, dict))

    def test_returns_expected_components(self):
        comps = walk_tree_for_components(self.tree, self.walker)
        self.equa(
            comps,
            {
                'type': 'Name',
                'props': {},
                'parts': []
            }
        )

class test_basic_tkml_tree_when_walked_for_components(Spec):
    def setUp(self):
        source = dedent('''
            Block {
                prop_1: "some string"
            }
        ''')
        self.tree = tkml_tree(source)
        self.walker = TKMLVisitor()

    def test_returns_expected_component_dict(self):
        comps = walk_tree_for_components(self.tree, self.walker)
        self.equa(
            comps,
            {
                'type': 'Block',
                'props': {'prop_1': 'some string'},
                'parts': []
            }
        )

class test_medium_tkml_tree_when_walked_for_components(Spec):
    def setUp(self):
        source = dedent('''
            Block {
                int: 23
                float: 5.29
                string: "aim for the moon"
                string2: 'wind up among stars'
                multi: id: 2001
                color: #123ABC
            }
        ''')
        self.tree = tkml_tree(source)
        self.walker = TKMLVisitor()

    def test_returns_expected_component_dict(self):
        comps = walk_tree_for_components(self.tree, self.walker)
        self.equa(
            comps,
            {
                'type': 'Block',
                'props': {
                    'int': 23,
                    'float': 5.29,
                    'string': 'aim for the moon',
                    'string2': 'wind up among stars',
                    'multi': {'id': 2001},
                    'color': '#123ABC'
                },
                'parts': []
            }
        )

class test_example_tkml_tree_when_walked_for_components(Spec):
    def setUp(self):
        source = dedent('''
            Block {
                string: "a string value"
                number: 31
                float: 23.529
                color: #AA1122
                nested_block { v: #123ABC  q: 1000}
                nested_prop: v: #123456
                0: "digit identifier"
            }
        ''')
        self.tree = tkml_tree(source)
        self.walker = TKMLVisitor()

    def test_returns_expected_component_dict(self):
        comps = walk_tree_for_components(self.tree, self.walker)
        self.equa(
            comps,
            {
                'type': 'Block',
                'props': 
                    {
                        'string': 'a string value',
                        'number': 31,
                        'float': 23.529,
                        'color': '#AA1122',
                        'nested_prop': {'v': '#123456'},
                        '0': 'digit identifier',
                    },
                'parts': [
                    {
                        'type': 'nested_block',
                        'props': 
                            {
                                'q': 1000, 'v': '#123ABC'
                            },
                        'parts': [],
                    }
                ],
            }
        )
        

if __name__ == '__main__':
    main(testRunner=Runner)

