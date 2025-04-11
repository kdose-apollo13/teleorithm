"""
    |teleorithm|

    TODO: number include float in grammar
"""
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from parsimonious.exceptions import ParseError


# TODO: why nested r-strings?
grammar_text = r'''
tkml        = ws block ws
block       = identifier ws "{" ws item* ws "}"
item        = (property / block) ws
property    = identifier ws ":" ws value
value       = string / identifier / color / number
string      = ~r'"([^\n"\\]|(\\[^\\]))*"' / ~r"'([^\n'\\]|(\\[^\\]))*'"
identifier  = ~"[a-zA-Z_][a-zA-Z0-9_]*"
color       = "#" ~"[a-zA-Z0-9]{6}"
number      = ~"[0-9]+"
ws          = ~"\\s*"
'''

tkml_grammar = Grammar(grammar_text)


def parse_source(s, grammar):
    """
        s
            : str
            : tkml source text

        grammar
            : parsimonious.grammar.Grammar

        returns
            -> parsimonious.nodes.Node

        raises
            -> ValueError when parsing fails
    """
    try:
        tree = grammar.parse(s)
    except ParseError as e:
        raise ValueError(e)
    return tree


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


