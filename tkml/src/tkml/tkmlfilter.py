from parsimonious.nodes import NodeVisitor


class TKMLFilter(NodeVisitor):
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
        comptree = node_filter.visit(grammar_tree)
    except Exception as e:
        raise e
    else:
        return comptree


if __name__ == '__main__':
    
    pass
