"""
    | teleorithm |
"""
from parsimonious.grammar import Grammar
from parsimonious.exceptions import ParseError


# TODO: analyze for associativity problems
# TODO: encompass unicode?
TKML_GRAMMAR = r'''
tkml            = ws block ws
block           = identifier ws "{" ws item* ws "}"
item            = (prop / block) ws
prop            = identifier ws ":" ws (nested_props / value) ws
nested_props    = "{" ws inner_prop* ws "}"
inner_prop      = identifier ws ":" ws value ws
value           = string / color / number / identifier
string          = ~r'"([^\n"\\]|(\\[^\\]))*"' / ~r"'([^\n'\\]|(\\[^\\]))*'"
color           = ~"#[a-zA-Z0-9]{6}"
number          = ~r"[0-9]+(\.[0-9]+)?"
identifier      = ~r"[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)*" 
ws              = ~"\\s*"
'''
# order matters -> (x / y / z) will disambiguate by first match
# TKML_GRAMMAR = r'''
# tkml        = ws block ws
# block       = identifier ws "{" ws item* ws "}"
# item        = (property / block) ws
# property    = identifier ws ":" ws (property / value)
# value       = number / color / identifier / string
# string      = ~r'"([^\n"\\]|(\\[^\\]))*"' / ~r"'([^\n'\\]|(\\[^\\]))*'"
# identifier  = ~r"[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)*" 
# color       = ~"#[a-zA-Z0-9]{6}"
# number      = ~r"[0-9]+(\.[0-9]+)*"
# ws          = ~"\\s*"
# '''

EXAMPLE_SOURCE = '''
Block {
    string: "a string value"
    number: 31
    float: 23.529
    color: #AA1122
    nested_block: { v: #123ABC  q: 1000}
    0: "digit identifier"
    one.two: "dotted identifer"
}
'''

class IGrammar(Grammar):
    """
        Grammar
            : parsimonious.grammar.Grammar
            : OrderedDict with regex powers to parse strings against rules
    """
    
    def __init__(self, definition):
        """
            definition
                : str
                : defines PEG grammar

            raises
                ! ValueError
        """
        try:
            super().__init__(definition)
        except ParseError as e:
            raise ValueError('definition could not be interpreted as grammar')

    def parse(self, source):
        """
            source
                : str
                : source text seeking classification according to rules
            
            returns
                > parsimonious.nodes.Node
                > root node of tree describing hierarchy of matched rules

            raises
                ! ValueError
        """
        try:
            tree = super().parse(source)
        except ParseError as e:
            raise ValueError('no path of acceptance was found for this source')
        else:
            return tree

def tkml_tree(source):
    """
        source
            : str
            : tkml-compliant source text

        returns
            > parsimonious.nodes.Node

        raises
            ! ValueError

    """
    tree = IGrammar(TKML_GRAMMAR).parse(source)
    return tree


if __name__ == '__main__':

    # source = 'Tkml {}'
    source = EXAMPLE_SOURCE
    tree = IGrammar(TKML_GRAMMAR).parse(source)
    assert tree.full_text == source
    assert tree.expr_name == 'tkml'
    assert tree.end == len(source)

    source = '23'
    grammar = IGrammar(TKML_GRAMMAR)
    tree = grammar['number'].parse(source)
    assert tree.full_text == source
    assert tree.expr_name == 'number'
    assert tree.end == len(source)

