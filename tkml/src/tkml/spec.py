"""
    |teleorithm|

    TODO: number include float in grammar
"""
from parsimonious.nodes import NodeVisitor

from tkml.grammar import grow_tree


class TKMLVisitor(NodeVisitor):
    def visit_tkml(self, node, visited):
        return visited[1]

    def visit_block(self, node, visited):
        name = visited[0]
        items = visited[4]  # item*
        props = {}
        children = []
        for item_list in items:
            if item_list:
                item = item_list[0]
                if isinstance(item, dict):
                    if "type" in item:
                        children.append(item)
                    else:
                        props.update(item)
        widget = {'type': name, 'props': props, 'children': children}
        return widget

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


if __name__ == '__main__':
    t = grow_tree('Name {}')
    spec = TKMLVisitor().visit(t)
    assert spec == {
        'type': 'Name',
        'props': {},
        'children': []
    }

