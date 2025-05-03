"""
    | teleorithm |

    remember a property is matched by identifer: thing
    not by number -> so 0: 1 in tkml becomes '0': 1
"""
from textwrap import dedent

from tkml.grammar import tkml_tree
from tkml.tkmlvisitor import TKMLVisitor
from tkml.utils import key_and_value


# these properties are defined as nested blocks to allow multiple key-value pairs
BLOCK_PROPS = [
    'bind', 'config', 'grid', 'grid_rowconfigure', 'grid_columnconfigure'
]


def move_block_props(component):
    """
        component
            : dict
            : { 
                'type': '', 
                'props': {}, 
                'parts': [{'type': 'config', 'props': {}, 'parts': []}, ...] 
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
        if (name := part['type']) in BLOCK_PROPS:
            prop = {name: part['props']}
            block_props.update(prop)

    new = dict(component)
    new['props'].update(block_props)
    new['parts'] = [c for c in parts if c['type'] not in BLOCK_PROPS]
    return new


def rebuild(component):
    """
        component
            : dict

        returns
            > dict
            > new component rearchitected including all nested parts
    """
    new = move_block_props(component)
    new['parts'] = [rebuild(c) for c in new['parts']]
    return new


if __name__ == '__main__':
    source = 'Tkml { config: 0: 1 background: #123456}'
    tree = tkml_tree(source)
    root = TKMLVisitor().visit(tree)
    wspec = rebuild(root)
    assert wspec == {
        'type': 'Tkml',
        'props': {'config': {'0': 1}, 'background': '#123456'},
        'parts': []
    }

