"""
    !kDoSE¡ -> before to proceed, ensure Tk and App are interchangeable
    (ie) allow tkinter widgets without wrapping in component

"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from textwrap import dedent
import tkinter
import tomllib

from tkml.grammar import tkml_tree
from tkml.tkmlvisitor import TKMLVisitor
from tkml.component import rebuild
from tkml.widget import apply_props
from tkml.errors import TkmlError
from tkml.utils import load_tkml_file, load_toml_file, key_and_value


class test_load_tkml_file_leafcomps(Spec):
    def setUp(self):
        self.path = 'leafcomps.tkml'

    def test_returns_string(self):
        self.maxDiff = None
        s = load_tkml_file(self.path)
        self.asrt(isinstance(s, str))

        self.equa(
            s,
            dedent('''\
            _ {
                App {
                    Tk {
                        id: root
                    }
                }

                Scrollable {
                    Frame {
                        id: container

                        Canvas {
                            id: viewport
                            config: yscrollcommand: scrollbar.set
                            create_window { xy: '0,0' window: 'content' anchor: 'nw' }

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

                Leaf {
                    Frame {
                        id: container

                        Canvas {
                            id: hili
                        }

                        Text {
                            id: textbox
                            text: 'cosmo! go!'
                        }
                    }
                }
            }
            ''')
        )


class test_tkml_tree_leafcomps(Spec):
    def setUp(self):
        path = 'leafcomps.tkml'
        tkml_string = load_tkml_file(path)
        node = tkml_tree(tkml_string)
        self.weird_component_hierarchy = TKMLVisitor().visit(node)

    def test_returns_component_hierarchy_dict(self):
        self.maxDiff = None
        component_hierarchy = rebuild(self.weird_component_hierarchy)
        self.asrt(isinstance(component_hierarchy, dict))
        
        # even a simple Scrollable is some incredible structure...
        self.equa(
            component_hierarchy,
            {
                'type': '_',
                'props': {},
                'parts': [
        # ---------------------------------------------------------------------
                    {
                        'type': 'App',
                        'props': {},
                        'parts': [
                            {
                                'type': 'Tk',
                                'props': {'id': 'root'},
                                'parts': []
                            }
                        ]
                    },
        # ---------------------------------------------------------------------
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
                                            'config': {'yscrollcommand': 'scrollbar.set'},
                                            'create_window': {
                                                'xy': '0,0',
                                                'window': 'content',
                                                'anchor': 'nw'
                                            }
                                        },
                                        'parts': [
                                            {
                                                'type': 'Frame',
                                                'props': {'id': 'content'},
                                                'parts': []
                                            }
                                        ]
                                    },
                                    {
                                        'type': 'Scrollbar',
                                        'props': {
                                            'id': 'scrollbar',
                                            'config': {'command': 'viewport.yview'}},
                                        'parts': []}
                                ]
                            }
                        ]
                    },
        # ---------------------------------------------------------------------
                    {
                        'type': 'Leaf',
                        'props': {},
                        'parts': [
                            {
                                'type': 'Frame',
                                'props': {'id': 'container'},
                                'parts': [
                                    {
                                        'type': 'Canvas',
                                        'props': {'id': 'hili'},
                                        'parts': []
                                    }, 
                                    {
                                        'type': 'Text',
                                        'props': {'id': 'textbox', 'text': 'cosmo! go!'},
                                        'parts': []
                                    }
                                ]
                            }
                        ]
                    }
        # ---------------------------------------------------------------------
                ]
            }
        )


class test_load_tkml_file_leafapp(Spec):
    def setUp(self):
        self.path = 'leafapp.tkml'

    def test_returns_string(self):
        self.maxDiff = None
        s = load_tkml_file(self.path)
        self.asrt(isinstance(s, str))

        self.equa(
            s,
            dedent('''\
            App {
                title: 'align failure successwise'
                geometry: '400x900'

                Scrollable {
                    Leaf { id: l1 }
                }
            }
            ''')
        )
    

class test_tkml_tree_leafapp(Spec):
    def setUp(self):
        path = 'leafapp.tkml'
        tkml_string = load_tkml_file(path)
        node = tkml_tree(tkml_string)
        self.weird_component_hierarchy = TKMLVisitor().visit(node)

    def test_returns_component_hierarchy_dict(self):
        self.maxDiff = None
        component_hierarchy = rebuild(self.weird_component_hierarchy)
        self.asrt(isinstance(component_hierarchy, dict))
        
        # even a simple Scrollable is some incredible structure...
        self.equa(
            component_hierarchy,
            {
                'type': 'App',
                'props': {'geometry': '400x900', 'title': 'align failure successwise'},
                'parts': [
                    {
                        'type': 'Scrollable',
                        'props': {},
                        'parts': [
                            {
                                'type': 'Leaf',
                                'parts': [],
                                'props': {'id': 'l1'},
                            }
                        ],
                    }
                ],
            }
        )


class test_load_toml_file_leafstyle(Spec):
    def setUp(self):
        self.path = 'leafstyle.toml'

    def test_returns_stated_style_hierarchy_dict(self):
        self.maxDiff = None
        stated_style_hierarchy = load_toml_file(self.path)
        self.asrt(isinstance(stated_style_hierarchy, dict))

        self.equa(
            stated_style_hierarchy,
            {
                'Default': {
                    'App': {
                        'geometry': '400x900', 'title': 'Failure is Inevitable'
                    },

                    'Leaf': {
                        'Frame': {
                            'config': {'bd': 2, 'relief': 'solid'},
                            'grid': {'column': 0, 'row': 0, 'sticky': 'nsew'},
                            'grid_columnconfigure': {'col': 0, 'weight': 1},
                            'grid_rowconfigure': {'row': 0, 'weight': 1},

                            'Canvas': {
                                'config': {'background': '#2299AA', 'width': 10},
                                'grid': {'column': 0, 'row': 0, 'sticky': 'ns'}
                            },

                            'Text': {
                                'config': {'height': 1, 'width': 20},
                                 'grid': {'column': 1, 'row': 0, 'sticky': 'nesw'},
                                 'text': 'hello'
                            },
                        }
                    },

                    'Scrollable': {
                        'Frame': {
                            'config': {'bd': 2, 'relief': 'solid'},
                            'grid': {'column': 0, 'row': 0, 'sticky': 'nsew'},
                            'grid_columnconfigure': {'col': 0, 'weight': 1},
                            'grid_rowconfigure': {'row': 0, 'weight': 1},

                            'Canvas': {
                                'config': {'yscrollcommand': 'scrollbar.set'},
                                'grid': {'column': 0, 'row': 0, 'sticky': 'nsew'},

                                'Frame': {
                                    'config': {},
                                    'grid_columnconfigure': {'col': 0, 'weight': 1}
                                },
                            },

                            'Scrollbar': {
                                'config': {'command': 'viewport.yview', 'orient': 'vertical'},
                                'grid': {'column': 1, 'row': 0, 'sticky': 'ns'}
                            },
                        }
                    }
                }
            }
        )
        



if __name__ == '__main__':
    main(testRunner=Runner)

