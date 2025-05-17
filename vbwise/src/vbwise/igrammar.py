"""
    | teleorithm |
"""
from parsimonious.grammar import Grammar
from parsimonious.exceptions import ParseError
from parsimonious.nodes import Node


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
            raise ValueError('no valid path for this source', e.pos)
        else:
            return tree


EXAMPLE_GRAMMAR = r'''
root = word / number
word = ~r'[a-zA-Z]+'
number = ~r'[0-9]+'
'''

if __name__ == '__main__':
    grammar = IGrammar(EXAMPLE_GRAMMAR)
    assert isinstance(grammar, Grammar)

    node = grammar.parse('blah')
    assert node.full_text == 'blah'
    assert node.expr_name == 'root'

    node = grammar.parse('24')
    assert node.full_text == '24'
    assert node.expr_name == 'root'

