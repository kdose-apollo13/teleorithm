"""
    tkml source -> grammar tree -> component tree -> widget tree (app)
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


def construct_grammar(source):
    """
        source
            : str

        returns
            -> parsimonious.grammar.Grammar

        raises
            -> ValueError
    """
    try:
        g = Grammar(source)
    except Exception as e:
        raise ValueError(e)
    else:
        return g


def parse_source(s, grammar):
    """
        s
            : str

        grammar
            : parsimonious.grammar.Grammar

        returns
            -> parsimonious.nodes.Node
            -> represents root of tree

        raises
            -> ValueError
    """
    try:
        tree = grammar.parse(s)
    except ParseError as e:
        raise ValueError(e)
    return tree


def grow_tree(source):
    """
        source
            : str
            : tkml source

        returns
            -> parsimonious.nodes.Node
            -> root node of tree of successful grammar matches

        raises
            -> ValueError if source was not valid according to present grammar
    """
    g = construct_grammar(TKML_GRAMMAR)
    tree = parse_source(source, g)
    return tree
    
if __name__ == '__main__':
    t = grow_tree('Name {}')
    print(t.prettily())

