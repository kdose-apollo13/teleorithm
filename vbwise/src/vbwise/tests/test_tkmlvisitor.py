"""
    | teleorithm |
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from textwrap import dedent

from vbwise.tkmlgrammar import tkml_tree
from vbwise.tkmlvisitor import TKMLVisitor


class test_single_and_multiline_sources(Spec):
    def setUp(self):
        self.single = 'Name {}'

        self.multi = dedent('''\
        Name {}''')

    def test_represent_same_value(self):
        self.equa(self.single, self.multi)

    def test_have_identical_trees(self):
        self.equa(
            tkml_tree(self.single),
            tkml_tree(self.multi)
        )
        

class test_trivial_tkml_tree_when_walked_for_components(Spec):
    def setUp(self):
        source = 'Name {}'
        self.tree = tkml_tree(source)

    def test_returns_dict(self):
        root = TKMLVisitor().visit(self.tree)
        self.asrt(isinstance(root, dict))

        self.equa(
            root,
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

    def test_returns_expected_component_dict(self):
        root = TKMLVisitor().visit(self.tree)
        self.equa(
            root,
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
                multi: { id: 2001 }
                color: #123ABC
            }
        ''')
        self.tree = tkml_tree(source)

    def test_returns_expected_component_dict(self):
        root = TKMLVisitor().visit(self.tree)
        self.maxDiff = None
        self.equa(
            root,
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
                nested_block { v: #123ABC q: 1000 }
                nested_prop: { v: #123456 q: 2000 }
                0: "digit identifier"
            }
        ''')
        self.tree = tkml_tree(source)

    def test_returns_expected_component_dict(self):
        root = TKMLVisitor().visit(self.tree)
        self.equa(
            root,
            {
                'type': 'Block',
                'props': 
                    {
                        'string': 'a string value',
                        'number': 31,
                        'float': 23.529,
                        'color': '#AA1122',
                        'nested_prop': {'v': '#123456', 'q': 2000},
                        0: 'digit identifier',
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
        

class test_nontrivial_source(Spec):
    def setUp(self):
        source = dedent('''
        App {
            script: 'app.py'
            style: 'app.toml'
            comps: 'app.tkml'

            Scrollable {
                Frame {
                    id: container
                    bind: { <Return>: whatever }

                    Canvas {
                        id: viewport
                        config: { yscrollcommand: 'scrollbar.set' }

                        Frame { 
                            id: content 
                        }
                    }

                    Scrollbar { 
                        id: scrollbar
                        config: { command: 'viewport.yview' }
                    }
                }
            }
        }
        ''')
        self.tree = tkml_tree(source)

    def test_achieves_expected_value(self):
        root = TKMLVisitor().visit(self.tree)

        self.equa(
            root,
            {
                'type': 'App',
                'props': {
                    'script': 'app.py', 'style': 'app.toml', 'comps': 'app.tkml'
                },
                'parts': [
                    {
                        'type': 'Scrollable',
                        'props': {},
                        'parts': [
                            {
                                'type': 'Frame',
                                'props': {
                                    'id': 'container',
                                    'bind': {'<Return>': 'whatever'}
                                },
                                'parts': [
                                    {
                                        'type': 'Canvas',
                                        'props': {
                                            'id': 'viewport',
                                            'config': {
                                                'yscrollcommand': 'scrollbar.set'
                                            }
                                        },
                                        'parts': [
                                            {
                                                'type': 'Frame',
                                                'props': {'id': 'content'},
                                                'parts': []}
                                        ]
                                    },
                                    {
                                        'type': 'Scrollbar',
                                        'props': {
                                            'id': 'scrollbar',
                                            'config': {'command': 'viewport.yview'}
                                        },
                                        'parts': []
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        )


if __name__ == '__main__':
    main(testRunner=Runner)

