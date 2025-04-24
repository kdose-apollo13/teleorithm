"""
    | teleorithm |
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from textwrap import dedent
from tkinter import *

from tkml.component import (
    comp_tree, comp_name_and_props, prop_tree_from_comp_tree, 
    style_props_and_script_props, SCRIPT_KEYS, MULTIPROP_NAMES
)
from tkml.utils import key_and_value_from


class Test_trivial_tkml_source(Spec):
    def setUp(self):
        self.source = dedent('''
            Scrollable { }
        ''')
        self.script_keys = SCRIPT_KEYS

    def test_to_comptree_returns_dict(self):
        comptree = comp_tree(self.source)

        self.asrt(isinstance(comptree, dict))

        self.equa(
            comptree,
            {'type': 'Scrollable', 'props': {}, 'parts': []}
        )

    def test_comptree_to_nameprops_returns_dict(self):
        comptree = comp_tree(self.source)
        nameprops = comp_name_and_props(comptree)

        self.asrt(isinstance(nameprops, dict))

        self.equa(
            nameprops,
            {'Scrollable': {}}
        )
        
    def test_nameprops_to_key_and_value_returns_tuple(self):
        comptree = comp_tree(self.source)
        nameprops = comp_name_and_props(comptree)
        t = key_and_value_from(nameprops)
        self.asrt(isinstance(t, tuple))

        name, props = t
        self.asrt(isinstance(name, str))
        self.asrt(isinstance(props, dict))

        self.equa(name, 'Scrollable')
        self.equa(props, {})
    
    def test_props_to_style_and_script_specific_props(self):
        comptree = comp_tree(self.source)
        nameprops = comp_name_and_props(comptree)
        name, props = key_and_value_from(nameprops)
        
        styl, scrip = style_props_and_script_props(props, self.script_keys)
        
        self.equa(styl, {})
        self.equa(scrip, {})
   

class Test_tkml_source_with_style_and_script_props(Spec):
    def setUp(self):
        self.source = dedent('''
            Scrollable {
                id: w23
                config { key: 'value' }
                bind { event: 'script.callback' }
                bg: #123123
                grid { row: 0 column: 0 }
            }
        ''')

    def test_to_comptree_returns_dict(self):
        comptree = comp_tree(self.source)

        self.asrt(isinstance(comptree, dict))

        self.equa(
            comptree,
            {
                'type': 'Scrollable',
                'props': {
                    'id': 'w23',
                    'config': {'key': 'value'},
                    'bind': {'event': 'script.callback'},
                    'bg': '#123123',
                    'grid': {'column': 0, 'row': 0},
                },
                'parts': [],
            }

        )

    def test_comptree_to_nameprops_returns_dict(self):
        comptree = comp_tree(self.source)
        nameprops = comp_name_and_props(comptree)

        self.asrt(isinstance(nameprops, dict))

        self.equa(
            nameprops,
            {
                'Scrollable': {
                    'id': 'w23',
                    'config': {'key': 'value'},
                    'bind': {'event': 'script.callback'},
                    'bg': '#123123',
                    'grid': {'column': 0, 'row': 0},
                }
            }
        )

    def test_separating_style_and_script_props_returns_tuple_of_dict(self):
        comptree = comp_tree(self.source)
        nameprops = comp_name_and_props(comptree)
        name, props = key_and_value_from(nameprops)
        t = style_props_and_script_props(props, SCRIPT_KEYS)

        self.asrt(isinstance(t, tuple))
        
        style, scrip = t

        self.asrt(isinstance(style, dict))
        self.asrt(isinstance(scrip, dict))

        self.equa(
            style,
            {
                'bg': '#123123',
                'grid': {'column': 0, 'row': 0},
            }
        )

        self.equa(
            scrip,
            {
                'id': 'w23',
                'config': {'key': 'value'},
                'bind': {'event': 'script.callback'},
            }
        )

    def test_comp_tree_to_prop_tree_returns_dict(self):
        comptree = comp_tree(self.source)
        tree = prop_tree_from_comp_tree(comptree)

        self.equa(
            tree,
            {
                'type': 'Scrollable',
                'script_props': {
                    'id': 'w23',
                    'bind': {'event': 'script.callback'},
                    'config': {'key': 'value'},
                },
                'style_props': {
                    'bg': '#123123',
                    'grid': {'column': 0, 'row': 0}
                },
                'parts': [],
            }
        )



class Test_real_tkml_source_for_Scrollable(Spec):
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

    def test_to_comptree_returns_dict(self):
        comptree = comp_tree(self.source)

        self.asrt(isinstance(comptree, dict))

        # self.maxDiff = None
        self.equa(
            comptree,
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
                                    'config': {'yscrollcommand': 'scrollbar.set'},
                                    'id': 'viewport'
                                },
                                'parts': [
                                    {
                                        'type': 'Frame',
                                        'props': {'id': 'content'},
                                        'parts': [],
                                    }
                                ],
                            },
                            {
                                'type': 'Scrollbar',
                                'props': {
                                    'config': {'command': 'viewport.yview'},
                                    'id': 'scrollbar'
                                },
                                'parts': [],
                            }
                        ],
                    }
                ],
            }
        )

    def test_comp_tree_to_prop_tree_returns_dict(self):
        comptree = comp_tree(self.source)
        tree = prop_tree_from_comp_tree(comptree)

        self.equa(
            tree,
            {
                'type': 'Scrollable',
                'style_props': {},
                'script_props': {},
                'parts': [
                    {
                        'type': 'Frame',
                        'style_props': {},
                        'script_props': {'id': 'container'},
                        'parts': [
                            {
                                'type': 'Canvas',
                                'style_props': {},
                                'script_props': {
                                    'config': {'yscrollcommand': 'scrollbar.set'},
                                    'id': 'viewport'
                                },
                                'parts': [
                                    {
                                        'type': 'Frame',
                                        'style_props': {},
                                        'script_props': {'id': 'content'},
                                        'parts': [],
                                    }
                                ],
                            },
                            {
                                'type': 'Scrollbar',
                                'style_props': {},
                                'script_props': {
                                    'config': {'command': 'viewport.yview'},
                                    'id': 'scrollbar'
                                },
                                'parts': [],
                            }
                        ],
                    }
                ],
            }
        )



if __name__ == '__main__':
    main(testRunner=Runner)

