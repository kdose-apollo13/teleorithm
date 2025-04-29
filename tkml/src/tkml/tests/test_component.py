"""
    | teleorithm |
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from textwrap import dedent

from tkml.grammar import tkml_tree
from tkml.tkmlvisitor import TKMLVisitor
from tkml.component import rebuild


class test_full_rebuild_on_nontrivial_source(Spec):
    def setUp(self):
        source = dedent('''
        App {
            script: 'app.py'
            style: 'app.toml'
            comps: 'app.tkml'

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
        }
        ''')
        tree = tkml_tree(source)
        self.root = TKMLVisitor().visit(tree)

    def test_achieves_expected_value(self):
        wspec = rebuild(self.root)
        self.equa(
            wspec,
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
                                'props': {'id': 'container'},
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

