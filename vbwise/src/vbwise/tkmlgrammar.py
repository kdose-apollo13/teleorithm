"""
    | teleorithm |

    Tkinter Markup Language
"""
from parsimonious.grammar import Grammar
from parsimonious.nodes import Node

from igrammar import IGrammar


GRAMMAR = r'''
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

EXAMPLE_SOURCE = '''
Block {
    string: "a string value"
    number: 31
    float: 23.529
    color: #AA1122
    nested_prop: { v: #123ABC q: 1000 }
    nested_block {
        0: "digit identifier"
        one.two: "dotted identifer"
    }
}
'''

if __name__ == '__main__':
    root = IGrammar(GRAMMAR).parse(EXAMPLE_SOURCE)
    assert isinstance(root, Node)
    assert root.full_text == EXAMPLE_SOURCE
    assert root.expr_name == 'tkml'
    assert root.end == len(EXAMPLE_SOURCE)

    grammar = IGrammar(GRAMMAR)
    assert isinstance(grammar, Grammar)

    source = '2701'
    node = grammar['number'].parse(source)
    assert node.full_text == source
    assert node.expr_name == 'number'
    assert node.end == len(source)

