"""
    | teleorithm |

    in grammar, ( x / y ) induces a list
    that is why [0] in some visit methods
"""
from parsimonious.nodes import NodeVisitor
from parsimonious.exceptions import VisitationError

from vbwise.gnmlgrammar import gnml_tree, EXAMPLE_SOURCE


class GNMLVisitor(NodeVisitor):
    """
        knows how to walk gnml tree and extract nodes
        method -> .visit(Node)
    """
    def visit_gnml(self, node, visited):
        nodes = []
        if len(visited) > 1 and visited[1]:
            for node_def_result, _ in visited[1]:
                if node_def_result is not None:
                    nodes.append(node_def_result)
        return nodes

    def visit_node_def(self, node, visited):
        id_data = visited[2]
        content_data = visited[4]
        return {
            'id': id_data,
            'meta': content_data.get('meta', {}),
            'tags': content_data.get('tags', []),
            'next': content_data.get('next', []),
            'prev': content_data.get('prev', []),
            'text_lines': content_data.get('text_lines', []),
            'code_lines': content_data.get('code_lines', [])
        }

    def visit_node_start(self, node, visited):
        return None

    def visit_id_line(self, node, visited):
        return visited[6]

    def visit_content_lines(self, node, visited):
        content_data = {
            'meta': {},
            'tags': [],
            'next': [],
            'prev': [],
            'text_lines': [],
            'code_lines': []
        }
        for line_data in visited:
            if line_data:
                for key, value in line_data.items():
                    if isinstance(value, list):
                        content_data[key].extend(value)
                    else:
                        content_data[key].update(value)
        return content_data

    def visit_content_line(self, node, visited):
        return visited[0]

    def visit_meta_line(self, node, visited):
        kv_list_result = visited[6][0] if len(visited) > 6 and visited[6] else {}
        return {'meta': kv_list_result}

    def visit_tags_line(self, node, visited):
        id_list_result = visited[6][0] if len(visited) > 6 and visited[6] else []
        return {'tags': id_list_result}

    def visit_next_line(self, node, visited):
        complex_id_list_result = visited[6][0] if len(visited) > 6 and visited[6] else []
        return {'next': complex_id_list_result}

    def visit_prev_line(self, node, visited):
        complex_id_list_result = visited[6][0] if len(visited) > 6 and visited[6] else []
        return {'prev': complex_id_list_result}

    def visit_text_line(self, node, visited):
        level = visited[0]
        content = visited[3]
        return {'text_lines': [{'level': level, 'content': content}]}

    def visit_text_level(self, node, visited):
        return node.text

    def visit_text_content(self, node, visited):
        return node.text

    def visit_code_line(self, node, visited):
        level = visited[0]
        content = visited[3]
        return {'code_lines': [{'level': level, 'content': content}]}

    def visit_code_level(self, node, visited):
        return node.text

    def visit_code_content(self, node, visited):
        return node.text

    def visit_identifier_list(self, node, visited):
        identifiers = [visited[0]] if visited[0] is not None else []
        if len(visited) > 1 and visited[1]:
            for _, _, _, id_result in visited[1]:
                if id_result is not None:
                    identifiers.append(id_result)
        return identifiers

    def visit_key_value_list(self, node, visited):
        kv_dict = visited[0] or {}
        if len(visited) > 1 and visited[1]:
            for _, _, _, kv_result in visited[1]:
                if kv_result:
                    kv_dict.update(kv_result)
        return kv_dict

    def visit_key_value(self, node, visited):
        return {visited[0]: visited[4]}

    def visit_complex_identifier_list(self, node, visited):
        complex_identifiers = [visited[0]] if visited[0] is not None else []
        if len(visited) > 1 and visited[1]:
            for _, _, _, complex_id_result in visited[1]:
                if complex_id_result is not None:
                    complex_identifiers.append(complex_id_result)
        return complex_identifiers

    def visit_complex_identifier(self, node, visited):
        full_id = visited[0]
        if len(visited) > 1 and visited[1]:
            for _, id_result in visited[1]:
                if id_result is not None:
                    full_id += "." + id_result
        return full_id

    def visit_identifier(self, node, visited):
        return node.text

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
    tree = gnml_tree(EXAMPLE_SOURCE)
    nodes = GNMLVisitor().visit(tree)
    print(nodes)
    print(len(nodes))


