"""
    | teleorithm |

    TODO: number include float in grammar
"""
from parsimonious.nodes import NodeVisitor

from tkml.grammar import tkml_tree


class TKMLFilter(NodeVisitor):
    def visit_tkml(self, node, visited):
        return visited[1]

    def visit_block(self, node, visited):
        name = visited[0]
        items = visited[4]  # item*
        props = {}
        children = []
        # TODO: clean this up
        for item_list in items:
            if item_list:
                item = item_list[0]
                if isinstance(item, dict):
                    if "type" in item:
                        children.append(item)
                    else:
                        props.update(item)
        component = {'type': name, 'props': props, 'children': children}
        return component

    def visit_item(self, node, visited):
        return visited[0]

    def visit_property(self, node, visited):
        return {visited[0]: visited[4]}

    def visit_value(self, node, visited):
        return visited[0]

    def visit_string(self, node, visited):
        return node.text.strip('"')

    def visit_identifier(self, node, visited):
        return node.text

    def visit_color(self, node, visited):
        return node.text

    def visit_number(self, node, visited):
        return int(node.text)

    def generic_visit(self, node, visited):
        return visited or node.text


def comb_for_components(grammar_tree, node_filter):
    """
        grammar_tree
            : parsimonious.nodes.Node
        
        node_filter
            : parsimonious.nodes.NodeVisitor

        returns
            -> dict
    """
    try:
        comp_tree = node_filter.visit(grammar_tree)
    except Exception as e:
        raise e
    else:
        return comp_tree

if __name__ == '__main__':
    t = tkml_tree('Name {}')
    comps = comb_for_components(t, TKMLFilter())
    assert comps == {
        'type': 'Name',
        'props': {},
        'children': []
    }

