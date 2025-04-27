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
        component -> {'type': _, 'props': _, 'parts': _}
        use .visit(Node)
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

    def visit_property(self, node, visited):
        return {visited[0]: visited[4][0]}

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

            raises
                ! parsimonious.exceptions.VisitationError if catastrophic
                ! may succeed despite retrieving bad values

            returns
                > dict
                > root component - may contain nested components
        """
        try:
            root = super().visit(tree)
        except VisitationError as e:
            raise e
        else:
            return root


if __name__ == '__main__':
    from tkml.grammar import tkml_tree
    source = 'App { blah: 22.1 }'
    tree = tkml_tree(source)
    comps = TKMLVisitor().visit(tree)
    print(comps)


