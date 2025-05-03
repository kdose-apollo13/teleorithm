import tomllib

from parsimonious.grammar import Grammar
from parsimonious.nodes import Node, NodeVisitor
from parsimonious.exceptions import ParseError


def node_iter(node):
    """
        node
            : parsimonious.nodes.Node
            : or anything with .children iterable giving Nodes

        yields
            -> parsimonious.nodes.Node
    """
    stack = list()
    stack.append(node)
    found = []

    while len(stack) > 0:
        node = stack.pop()
        if isinstance(node, Node):
            found.append(node)
            stack.extend(n for n in node.children if not n in found)
            yield node


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


def load_toml_string(string):
    d = tomllib.loads(string)
    return d


def load_toml_file(path):
    with open(path, 'rb') as r:
        d = tomllib.load(r)
    return d


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


def overwrite_dict(d, e):
    """
        d
            : dict

        e
            : dict

        returns
            > dict
            > combined dicts with conflicts favoring e
    """
    new = {}
    for k, v in d.items():
        if isinstance(v, dict):
            # TODO: can get a TypeError here if e is not a dict
            # TODO: basically d and e must have same structure
            if k in e:
                new[k] = overwrite_dict(v, e[k])
            else:
                new[k] = v
        else:
            if k in e:
                new[k] = e[k]
            else:
                new[k] = v

    for k, v in e.items():
        if k not in d:
            new[k] = v

    return new
            


if __name__ == '__main__':
    
    from tkml.grammar import tkml_tree
    source = 'A { b: c }'
    tree = tkml_tree(source)
    assert count_nodes(tree) == 22
    assert count_nodes_another_way(tree) == 22

    #

    d = {'name': {'key': 'val'}}
    k, v = key_and_value(d)
    assert k == 'name'
    assert v == {'key': 'val'}
    
    #

    O = type('O', (), {'yeah': lambda self: print('hi')})

    s = 'whatever.yeah'
    d = {
        'whatever': O()
    }

    *keys, attr = split_keypath(s)
    y = return_by_keys(d, keys)
    assert hasattr(y, 'yeah')

    #

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

