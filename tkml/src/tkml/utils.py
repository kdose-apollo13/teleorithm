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


if __name__ == '__main__':
    from tkml.grammar import tkml_tree
    source = 'A { b: c }'
    tree = tkml_tree(source)
    assert count_nodes(tree) == 21
    assert count_nodes_another_way(tree) == 21
    
