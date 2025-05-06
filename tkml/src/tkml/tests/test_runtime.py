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
from tkml.errors import TkmlError
from tkml.utils import (
    load_tkml_file, load_toml_file, key_and_value, load_toml_string, overwrite_dict
)


types_and_methods = {
    'Tk': ['title', 'geometry'],
    'Frame': ['config'],
}


def merge_by_overwriting(style, layout):
    """
        style
            : dict
            : { type: '', props: {}, parts: []}

        layout
            : dict
            : { type: '', props: {}, parts: []}
        
        modifies
            ~ layout
    """
    new = overwrite_dict(style['props'], layout['props'])
    layout['props'] = new
    for sublayout in layout['parts']:
        for substyle in style['parts']:
            if substyle['type'] == sublayout['type']:
                merge_by_overwriting(substyle, sublayout)


def component_from_style(style_node):
    """
        style_node
            : dict

        returns
            > dict
    """
    new = {'type': '', 'props': {}, 'parts': []}

    for key, value in style_node.items():
        if key in types_and_methods:
            new['type'] = key
            for k, v in value.items():
                if k in types_and_methods:
                    new['parts'].append(component_from_style({k: v}))
                else:
                    new['props'].update({k: v})
        else:
            new['props'].update({key: value})
            
    return new


def component_hierarchy(tkml):
    """
        tkml
            : str

        returns
            > dict
    """
    node = tkml_tree(tkml)
    root = TKMLVisitor().visit(node)
    return root


class test_load_tkml_file_COMPONENTS(Spec):
    def setUp(self):
        self.path = '../components.tkml'

    def test_returns_tkml_string_defining_components_under_dummy_root(self):
        s = load_tkml_file(self.path)
        self.asrt(isinstance(s, str))

        self.equa(
            s,
            dedent('''\
            Components {

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
                            config: { yscrollcommand: scrollbar.set }
                            create_window: { x: 0 y: 0 window: content anchor: 'nw' }

                            Frame { 
                                id: content 
                            }
                        }

                        Scrollbar { 
                            id: scrollbar
                            config: { command: viewport.yview }
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


class test_component_hierarchy_COMPONENTS(Spec):
    def setUp(self):
        path = '../components.tkml'
        self.tkml_string = load_tkml_file(path)

    def test_returns_nested_dicts_of_type_props_parts(self):
        root = component_hierarchy(self.tkml_string)
        self.asrt(isinstance(root, dict))
        
        # even a simple Scrollable is some incredible structure...
        self.equa(
            root,
            {
                'type': 'Components',
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
                                                'x': 0,
                                                'y': 0,
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


class test_load_tkml_file_LAYOUT(Spec):
    def setUp(self):
        self.path = '../layout.tkml'

    def test_returns_tkml_string_defining_root_component_App(self):
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
    

class test_component_hierarchy_LAYOUT(Spec):
    def setUp(self):
        path = '../layout.tkml'
        self.tkml_string = load_tkml_file(path)

    def test_returns_nested_dicts_of_type_props_parts(self):
        root = component_hierarchy(self.tkml_string)
        self.asrt(isinstance(root, dict))
        
        self.equa(
            root,
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
                                'props': {'id': 'l1'},
                                'parts': [],
                            }
                        ],
                    }
                ],
            }
        )


class test_load_toml_file_STYLE(Spec):
    def setUp(self):
        self.path = '../style.toml'

    def test_returns_dict_of_component_styles_by_state(self):
        style_tree_by_state = load_toml_file(self.path)
        self.asrt(isinstance(style_tree_by_state, dict))

        self.equa(
            style_tree_by_state,
            {
                'Default': {
                    'App': {
                        'Tk': {
                            'title': 'Failure is Inconceivable',
                            'geometry': '400x900',
                        }
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


class test_trivial_layout_identical_inline_and_style(Spec):
    def setUp(self):
        self.layout = dedent('''
            Tk { 
                geometry: "100x100" 

                Frame {
                    config: { relief: "raised" }
                }
            }
        ''')
        self.style = dedent('''
            [Default]
            Tk.geometry = "400x900"
            Tk.Frame.config = { relief = 'groove' }
        ''')

    def test_inline_takes_precedence_over_style(self):
        layout_component_tree = component_hierarchy(self.layout)
        styles = load_toml_string(self.style)
        style = styles.get('Default', {})
        style_component_tree = component_from_style(style)
        merge_by_overwriting(style_component_tree, layout_component_tree)

        self.equa(
            layout_component_tree,
            {
                'type': 'Tk',
                'props': {'geometry': '100x100'},
                'parts': [
                    {
                        'type': 'Frame',
                        'props': {'config': {'relief': 'raised'}},
                        'parts': [],
                    }
                ],
            }
        )


class test_trivial_layout_no_geometry_inline_prop(Spec):
    def setUp(self):
        self.layout = dedent('''
            Tk { 
                Frame {
                    config: { relief: "raised" }
                }
            }
        ''')
        self.style = dedent('''
            [Default]
            Tk.geometry = "400x900"
            Tk.Frame.config = { relief = 'groove' }
        ''')
        comps = ''
        script = ''

    def test_style_overrides_absent_geometry_prop(self):
        layout_component_tree = component_hierarchy(self.layout)
        styles = load_toml_string(self.style)
        style = styles.get('Default', {})
        style_component_tree = component_from_style(style)
        merge_by_overwriting(style_component_tree, layout_component_tree)

        self.equa(
            layout_component_tree,
            {
                'type': 'Tk',
                'props': {'geometry': '400x900'},
                'parts': [
                    {
                        'type': 'Frame',
                        'props': {'config': {'relief': 'raised'}},
                        'parts': [],
                    }
                ],
            }
        )

class test_trivial_layout_no_Frame_config_nested_inline_prop(Spec):
    def setUp(self):
        self.layout = dedent('''
            Tk { 
                Frame {}
            }
        ''')
        self.style = dedent('''
            [Default]
            Tk.geometry = "400x900"
            Tk.Frame.config = { relief = 'groove' }
        ''')

    def test_style_overrides_absent_inline_prop(self):
        layout_component_tree = component_hierarchy(self.layout)
        styles = load_toml_string(self.style)
        style = styles.get('Default', {})
        style_component_tree = component_from_style(style)
        merge_by_overwriting(style_component_tree, layout_component_tree)

        self.equa(
            layout_component_tree,
            {
                'type': 'Tk',
                'props': {'geometry': '400x900'},
                'parts': [
                    {
                        'type': 'Frame',
                        'props': {'config': {'relief': 'groove'}},
                        'parts': [],
                    }
                ],
            }
        )


class test_trivial_layout_no_style(Spec):
    def setUp(self):
        self.layout = dedent('''
            Tk { 
                geometry: "100x100" 

                Frame {
                    config: { relief: "raised" }
                }
            }
        ''')
        self.style = dedent('''
        ''')

    def test_inline_works_as_expected(self):
        layout_component_tree = component_hierarchy(self.layout)
        styles = load_toml_string(self.style)
        style = styles.get('Default', {})
        style_component_tree = component_from_style(style)
        merge_by_overwriting(style_component_tree, layout_component_tree)

        self.equa(
            layout_component_tree,
            {
                'type': 'Tk',
                'props': {'geometry': '100x100'},
                'parts': [
                    {
                        'type': 'Frame',
                        'props': {'config': {'relief': 'raised'}},
                        'parts': [],
                    }
                ],
            }
        )


if __name__ == '__main__':
    main(testRunner=Runner)

