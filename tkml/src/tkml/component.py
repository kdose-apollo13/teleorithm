"""
    | teleorithm |

    remember a property is matched by identifer: thing
    not by number -> so 0: 1 in tkml becomes '0': 1
"""
from textwrap import dedent

from tkml.grammar import tkml_tree
from tkml.tkmlvisitor import TKMLVisitor
from tkml.utils import key_and_value


# in tkml these properties are defined as nested blocks
# to allow multiple key-value pairs
MULTIPROP_NAMES = [
    'bind', 'config', 'grid', 'grid_rowconfigure', 'grid_columnconfigure'
]

# for splitting props into style and script
SCRIPT_KEYS = [
    'id', 'bind', 'config'
]


def move_block_props(component):
    """
        component
            : dict
            : { 
                'type': '', 
                'props': {}, 
                'parts': [{'type': 'config', 'props': {}, parts: []}, ...] 
              }
        
        returns
            > dict
            > {
                'type': '',
                'props': {'config': {}},
                'parts': []
              }
    """
    _, props = key_and_value(component)
    parts = component['parts']

    block_props = {}

    for part in parts:
        if (n := part['type']) in MULTIPROP_NAMES:
            prop = {n: part['props']}
            block_props.update(prop)

    new = dict(component)
    new['props'].update(block_props)
    new['parts'] = [c for c in parts if c['type'] not in MULTIPROP_NAMES]
    return new


def split_props(props):
    """
        props
            : dict

        returns
            > tuple[dict]
            > script props, style props
    """
    script = {k: v for k, v in props.items() if k in SCRIPT_KEYS}
    style = {k: v for k, v in props.items() if k not in SCRIPT_KEYS}
    return script, style


def separate_props(component, script, style):
    """
        component
            : dict

        script
            : dict

        style
            : dict

        returns
            > dict
            > new component with props split into script and style specific
    """
    new = {}
    new['type'] = component['type']
    new['script_props'] = script
    new['style_props'] = style
    new['parts'] = component['parts']
    return new


def rebuild(component):
    """
        component
            : dict

        returns
            > dict
            > new component rearchitected including all nested parts
    """
    restructured = move_block_props(component)
    script, style = split_props(restructured['props'])
    new = separate_props(restructured, script, style)
    new['parts'] = [rebuild(c) for c in new['parts']]
    return new


if __name__ == '__main__':
    source = 'Tkml { config: 0: 1 background: #123456}'
    tree = tkml_tree(source)
    root = TKMLVisitor().visit(tree)
    widget_ready = rebuild(root)
    assert widget_ready == {
        'type': 'Tkml',
        'script_props': {'config': {'0': 1}},
        'style_props': {'background': '#123456'},
        'parts': []
    }

