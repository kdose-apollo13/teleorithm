"""
    | teleorithm |

    in grammar, ( x / y ) induces a list
    that is why [0] in some visit methods
"""
from parsimonious.nodes import NodeVisitor
from parsimonious.exceptions import VisitationError


class TKMLVisitor(NodeVisitor):
    """
        knows how to walk tkml tree and extract components
        method -> .visit(Node)
    """
    def visit_tkml(self, node, visited):
        return visited[1]

    def visit_block(self, node, visited):
        name = visited[0]
        items = visited[4]  # item*
        props = {}
        parts = []
        for item in items:
            if isinstance(item, dict):
                if "type" in item:
                    parts.append(item)
                else:
                    props.update(item)
        component = {'type': name, 'props': props, 'parts': parts}
        return component

    def visit_item(self, node, visited):
        return visited[0][0]

    def visit_prop(self, node, visited):
        identifier = visited[0]
        value_or_nested_props = visited[4][0]

        if isinstance(value_or_nested_props, dict):
            return {identifier: value_or_nested_props}
        else:
            return {identifier: value_or_nested_props}

    def visit_nested_props(self, node, visited):
        inner_props_list = visited[2]
        nested_props_dict = {}
        for inner_prop_item in inner_props_list:
                 nested_props_dict.update(inner_prop_item)
        return nested_props_dict

    def visit_inner_prop(self, node, visited):
        identifier = visited[0]
        value = visited[4]
        return {identifier: value}

    def visit_value(self, node, visited):
        return visited[0]

    def visit_string(self, node, visited):
        t = node.text
        if t.startswith('"'):
            return t.strip('"')
        else:
            return t.strip("'")

    def visit_identifier(self, node, visited):
        return node.text

    def visit_color(self, node, visited):
        return node.text

    def visit_number(self, node, visited):
        t = node.text
        if '.' in t:
            return float(t)
        else:
            return int(t)

    def generic_visit(self, node, visited):
        return visited or node.text

    def visit(self, tree):
        """
            tree
                : parsimonious.nodes.Node

            returns
                > dict
                > root component - may contain nested components

            raises
                ! parsimonious.exceptions.VisitationError if catastrophic
                ! may succeed despite retrieving bad values
        """
        try:
            root = super().visit(tree)
        except VisitationError as e:
            raise e
        else:
            return root


if __name__ == '__main__':
    from tkml.grammar import tkml_tree
    source = 'App { blah: { thing: 22.1 }}'
    tree = tkml_tree(source)
    comps = TKMLVisitor().visit(tree)
    print(comps)


