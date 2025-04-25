"""
    | teleorithm |

    remember a property is matched by identifer: thing
    not by number -> so 0: 1 in tkml becomes '0': 1
"""
from textwrap import dedent

from parsimonious.nodes import NodeVisitor

from tkml.grammar import tkml_tree


from tkml.tkmlvisitor import walk_tree_for_components, TKMLVisitor
from tkml.utils import key_and_value_from


# in tkml these properties are defined as nested blocks
# to allow multiple key-value pairs
MULTIPROP_NAMES = ['bind', 'config', 'grid']

# for splitting props into style and script
SCRIPT_KEYS = ['id', 'bind', 'config']


def translate_blockdefined_props(comptree):
    """
        comptree
            : dict
            : {
                'type': '', 
                'props': {}, 
                'parts': [{'type': 'config', 'props': {}, parts: []}, ...]
            }

        returns
            -> dict
            -> {
                'type': '',
                'props': {'config': {}},
                'parts': []
            }
    """
    name, props = key_and_value_from(comptree)
    parts = comptree['parts']

    block_props = {}
    
    for part in parts:
        if (n := part['type']) in MULTIPROP_NAMES:
            prop = {n: part['props']}
            block_props.update(prop)
    
    new_comptree = {}
    new_comptree['type'] = comptree['type']
    new_comptree['props'] = comptree['props']
    new_comptree['parts'] = [p for p in parts if p['type'] not in MULTIPROP_NAMES]
    new_comptree['props'].update(block_props)
    return new_comptree


def comp_tree(source):
    """
        source
            : str
            : tkml source text

        returns
            -> dict
            -> {'type': '', 'props': {}, 'parts': []}
    """
    tree = tkml_tree(source)
    wild_comp_tree = walk_tree_for_components(tree, TKMLVisitor())
    refined_comp_tree = translate_blockdefined_props(wild_comp_tree)
    return refined_comp_tree


def comp_name_and_props(comptree):
    """
        comptree
            : dict
            : {'type': '', 'props': {}, 'parts': []}

        returns
            -> dict
            -> {name: {prop: val, ...}}
            -> maps type of component to its properties
    """
    d = {comptree['type']: comptree['props']}
    return d


def style_props_and_script_props(props, script_keys):
    """
        props
            : dict
            : {prop: val, ...}

        script_keys
            : list[str]
            : ['id', 'config', 'bind', ...]

        returns
            -> tuple[dict, dict]
            -> style props, script props
    """
    style_props = {}
    script_props = {}

    for k, v in props.items():
        if k in script_keys:
            script_props.update({k: v})
        else:
            style_props.update({k: v})

    return style_props, script_props 


def prop_tree_from_comp_tree(comptree):
    """
        comptree
            : dict

        returns
            -> dict
    """
    nameprops = comp_name_and_props(comptree)
    name, props = key_and_value_from(nameprops)
    style, scrip = style_props_and_script_props(props, SCRIPT_KEYS)
    tree = {}
    tree['type'] = comptree['type']
    tree['style_props'] = style
    tree['script_props'] = scrip
    tree['parts'] = [prop_tree_from_comp_tree(p) for p in comptree['parts']]
    return tree


if __name__ == '__main__':
    
    multiprop = 'Tkml { config: 0: 1 }'
    multitree = comp_tree(multiprop)
    assert multitree == {
        'type': 'Tkml',
        'props': {
            'config': {'0': 1}
        },
        'parts': []
    }

    blockprop = 'Tkml { config { 0: 1 }}'
    blocktree = comp_tree(blockprop)
    assert blocktree == multitree

    # ---------
    # ---------

    source = 'Scrollable {id: w23 bg: #123123}'
    comptree = comp_tree(source)
    assert comptree == {
        'type': 'Scrollable',
        'props': {'id': 'w23', 'bg': '#123123'},
        'parts': []
    }

    proptree = prop_tree_from_comp_tree(comptree)
    assert proptree == {
        'type': 'Scrollable',
        'style_props': {'bg': '#123123'},
        'script_props': {'id': 'w23'},
        'parts': []
    }

