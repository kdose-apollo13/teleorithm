"""
    | teleorithm |
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from textwrap import dedent

from tkml.grammar import tkml_tree
from tkml.tkmlvisitor import TKMLVisitor
from tkml.component import (
    move_block_props, split_props, separate_props, rebuild,
    MULTIPROP_NAMES, SCRIPT_KEYS
)
from tkml.utils import key_and_value


class test_multiprop_with_one_keyval_parsed_as_tkml_block(Spec):
    def setUp(self):
        source = dedent('''
            Tkml {
                config { 0: 'yeah' }
            }
        ''')
        tree = tkml_tree(source)
        self.root = TKMLVisitor().visit(tree)

    def test_becomes_typical_component_property(self):
        
        self.equa(
            self.root,
            {
                'type': 'Tkml',
                'props': {},
                'parts': [
                    {'type': 'config', 'props': {'0': 'yeah'}, 'parts': []}
                ]
            }
        )

        restructured_root = move_block_props(self.root)

        self.equa(
            restructured_root ,
            {
                'type': 'Tkml',
                'props': {'config': {'0': 'yeah'}},
                'parts': []
            }
        )


class test_multiprop_with_two_keyvals_parsed_as_tkml_block(Spec):
    def setUp(self):
        source = dedent('''
            Tkml {
                config { 0: 'yeah' 1: 'no' }
            }
        ''')
        tree = tkml_tree(source)
        self.root = TKMLVisitor().visit(tree)

    def test_becomes_typical_component_property(self):
        self.equa(
            self.root,
            {
                'type': 'Tkml',
                'props': {},
                'parts': [
                    {
                        'type': 'config',
                        'props': {'0': 'yeah', '1': 'no'},
                        'parts': []
                    }
                ]
            }
        )

        restructured_root = move_block_props(self.root)

        self.equa(
            restructured_root ,
            {
                'type': 'Tkml',
                'props': {'config': {'0': 'yeah', '1': 'no'}},
                'parts': []
            }
        )


class test_component_with_both_script_and_style_prop(Spec):
    def setUp(self):
        source = dedent('''
            Tkml {
                config { 0: 'yeah' 1: 'no' }
                background: #123456
            }
        ''')
        tree = tkml_tree(source)
        root = TKMLVisitor().visit(tree)
        self.component = move_block_props(root)

    def test_splits_into_two_dicts(self):
        script, style = split_props(self.component['props'])

        self.equa(
            script,
            {'config': {'0': 'yeah', '1': 'no'}}
        )

        self.equa(
            style,
            {'background': '#123456'}
        )

    def test_achieves_expected_rebuilt_component(self):
        script, style = split_props(self.component['props'])
        new = separate_props(self.component, script, style)

        self.equa(
            new,
            {
                'type': 'Tkml',
                'script_props': {'config': {'0': 'yeah', '1': 'no'}},
                'style_props': {'background': '#123456'},
                'parts' : []
            }
        )


class test_full_rebuild_on_nontrivial_source(Spec):
    def setUp(self):
        self.source = dedent('''
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

    def test_achieves_expected_value(self):
        tree = tkml_tree(self.source)
        root = TKMLVisitor().visit(tree)
        widget_ready = rebuild(root)

        self.equa(
            widget_ready,
            {
                'type': 'Scrollable',
                'script_props': {},
                'style_props': {},
                'parts': [
                    {
                        'type': 'Frame',
                        'script_props': {'id': 'container'},
                        'style_props': {},
                        'parts': [
                            {
                                'type': 'Canvas',
                                'script_props': {
                                    'id': 'viewport',
                                    'config': {'yscrollcommand': 'scrollbar.set'}
                                },
                                'style_props': {},
                                'parts': [
                                    {
                                        'type': 'Frame',
                                        'script_props': {'id': 'content'},
                                        'style_props': {},
                                        'parts': []
                                    }
                                ]
                            }, 
                            {
                                'type': 'Scrollbar',
                                'script_props': {
                                    'id': 'scrollbar',
                                    'config': {'command': 'viewport.yview'}},
                                'style_props': {},
                                'parts': []
                            }
                        ]
                    }
                ]
            }
        )
        

if __name__ == '__main__':
    main(testRunner=Runner)

