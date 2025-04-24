"""
    | teleorithm |
"""
from parsimonious.grammar import Grammar
from parsimonious.exceptions import ParseError


# TODO: encompass unicode?

# order matters -> (x / y / z) will disambiguate if multiply matched
TKML_GRAMMAR = r'''
tkml        = ws block ws
block       = identifier ws "{" ws item* ws "}"
item        = (property / block) ws
property    = identifier ws ":" ws (property / value)
value       = number / color / identifier / string
string      = ~r'"([^\n"\\]|(\\[^\\]))*"' / ~r"'([^\n'\\]|(\\[^\\]))*'"
identifier  = ~r"[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)*" 
color       = "#" ~"[a-zA-Z0-9]{6}"
number      = ~r"[0-9]+(\.[0-9]+)*"
ws          = ~"\\s*"
'''

EXAMPLE_SOURCE = '''
Block {
    string: "a string value"
    number: 31
    float: 23.529
    color: #AA1122
    nested_block { v: #123ABC  q: 1000}
    nested_prop: v: #123456
    0: "digit identifier"
}
'''


def grammify(s):
    """
        s
            : str
            : PEG grammar

        returns
            -> parsimonious.grammar.Grammar

        raises
            -> ValueError
    """
    try:
        g = Grammar(s)
    except Exception as e:
        raise ValueError(e)
    else:
        return g


def parse(source, grammar):
    """
        source
            : str
            : grammar-compliant source text

        grammar
            : parsimonious.grammar.Grammar

        returns
            -> parsimonious.nodes.Node
            -> represents root of tree

        raises
            -> ValueError
    """
    try:
        tree = grammar.parse(source)
    except ParseError as e:
        raise ValueError(e)
    return tree


def tkml_tree(source):
    """
        source
            : str

        returns
            -> parsimonious.nodes.Node
    """
    return parse(source, grammify(TKML_GRAMMAR))


if __name__ == '__main__':
    grammar = grammify(TKML_GRAMMAR)
    n = grammar['number'].parse('23')
    assert n.full_text == '23'

    node = parse(EXAMPLE_SOURCE, grammify(TKML_GRAMMAR))
    tree = tkml_tree(EXAMPLE_SOURCE)
    assert node == tree
    assert tree.full_text == EXAMPLE_SOURCE

