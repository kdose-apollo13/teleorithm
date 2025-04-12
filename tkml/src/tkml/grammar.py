"""
    | teleorithm |

    source -> grammar tree -> component tree -> widget tree (app)
    tkml   -> tkml tree    -> component tree -> widget tree (app)
"""
from parsimonious.grammar import Grammar
from parsimonious.exceptions import ParseError


# TODO: what is equivalent without nested r-strings? even though they're incredible
TKML_GRAMMAR = r'''
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

EXAMPLE_SOURCE = '''
Block {
    a_string: "a string value"
    a_number: 31
    Nested { v: #123ABC }
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
    return parse(source, grammify(TKML_GRAMMAR))


if __name__ == '__main__':
    node = parse(EXAMPLE_SOURCE, grammify(TKML_GRAMMAR))
    tree = tkml_tree(EXAMPLE_SOURCE)
    assert node == tree

