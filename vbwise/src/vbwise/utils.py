import tomllib

from parsimonious.grammar import Grammar
from parsimonious.nodes import Node, NodeVisitor
from parsimonious.exceptions import ParseError


def node_iter(root):
    """
        root
            : parsimonious.nodes.Node
            : or anything with .children iterable giving Nodes

        yields
            -> parsimonious.nodes.Node
    """
    stack = []
    stack.append(root)
    found = []

    while len(stack) > 0:
        node = stack.pop()
        if isinstance(node, Node):
            found.append(node)
            stack.extend(n for n in node.children if not n in found)

    yield from found


def count_nodes(tree):
    """
        tree
            : parsimonious.nodes.Node
            : root

        returns
            -> int
    """
    return sum(1 for _ in node_iter(tree))


def count_nodes_another_way(tree):
    """
        tree
            : parsimonious.nodes.Node
            : root

        returns
            -> int
    """
    tree_text = tree.prettily()
    return len(tree_text.splitlines())


def key_and_value(d):
    """
        d
            : dict
            : {'Scrollable': {prop: val, ...}}

        returns
            -> tuple[str, dict]
            -> 'Scrollable', {prop: val, ...}
            -> name of component mapped to its props
    """
    name, props = list(d.items())[0]
    return name, props
    

def split_keypath(s):
    """
        s
            : str
            : 'key1.key2. ... .keyN'

        returns
            -> ['key1', 'key2', ..., 'keyN']
    """
    return s.split('.')


def return_by_keys(d, keys):
    """
        d
            : dict
            : {'key1': 'key2': ... 'keyN': object}

        keys
            : list
            : ['key1', 'key2', ..., 'keyN']

        returns
            > object
            > d[key1][key2]...[keyN]
    """
    for key in keys:
        d = d[key]

    return d


def merge_dicts(a, b):
    """
    Return new dict merging a and b deeply.
    Values in b overwrite those in a.
    Neither a nor b is mutated.
    """
    result = {}
    for key in set(a) | set(b):
        in_a = key in a
        in_b = key in b
        if in_a and in_b:
            va, vb = a[key], b[key]
            # recurse if both dicts
            if isinstance(va, dict) and isinstance(vb, dict):
                result[key] = merge_dicts(va, vb)
            else:
                result[key] = vb
        elif in_b:
            vb = b[key]
            result[key] = merge_dicts({}, vb) if isinstance(vb, dict) else vb
        else:
            va = a[key]
            result[key] = merge_dicts({}, va) if isinstance(va, dict) else va

    return result


if __name__ == '__main__':
    
    from tkmlgrammar import tkml_tree
    source = 'A { b: c }'
    tree = tkml_tree(source)
    assert count_nodes(tree) == 22
    assert count_nodes_another_way(tree) == 23


    d = {'name': {'key': 'val'}}
    k, v = key_and_value(d)
    assert k == 'name'
    assert v == {'key': 'val'}
    

    O = type('O', (), {'yeah': lambda self: print('hi')})

    s = 'whatever.yeah'
    d = {
        'whatever': O()
    }

    *keys, attr = split_keypath(s)
    y = return_by_keys(d, keys)
    assert hasattr(y, 'yeah')


    s = 'one.two.three.four.thing'
    *keys, attr = split_keypath(s)
    d = {
        'one': {
            'two': {
                'three': {
                    'four': O()
                }
            }
        }
    }

    y = return_by_keys(d, keys)
    assert hasattr(y, 'yeah')

