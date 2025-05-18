"""
    | teleorithm |

    Tkinter Markup Language
"""
from parsimonious.grammar import Grammar
from parsimonious.nodes import Node

from vbwise.igrammar import IGrammar


TKML_GRAMMAR = r"""
    tkml                = _ block _
    block               = identifier _ LBRACE _ block_member_list _ RBRACE
    block_member_list   = (block_member_entry)*
    block_member_entry  = block_member _ (COMMA _)?
    block_member        = block / prop
    prop                = identifier _ COLON _ value
    value               = prop_group / identifier / string / color
    prop_group          = LBRACE _ prop_entry_list _ RBRACE
    prop_entry_list     = (prop_entry_item)*
    prop_entry_item     = prop_entry _ (COMMA _)?
    prop_entry          = identifier _ COLON _ value
    LBRACE              = "{"
    RBRACE              = "}"
    COLON               = ":"
    COMMA               = ","

    string              = ~r'"([^"\\]|\\.)*"' / ~r"'([^'\\]|\\.)*'"
    color               = ~r"#[a-fA-F0-9]{6}"
    number              = ~r"-?[0-9]+(\.[0-9]+)?"
    identifier          = ~r"[a-zA-Z0-9_<>-]+(\.[a-zA-Z0-9_<>.-]+)*"
    
    _                   = (ws / comment)*
    ws                  = ~r"\s+"

    # giant negative lookahead -> looks for color + delimiter
    # so a comment is # followed by 'not a color'
    comment             = ~r"#(?![a-fA-F0-9]{6}(?:$|\s|,|\}|#))[^\n]*"
"""


SOURCE = '''
Block {
    # comment line
    NestedBlock {}  # with trailing comment

    string: 'a "string" value'
    escaped: "what about \\"this\\" huh?"
    number: 31
    float: 23.529
    color: #AA1122
    dotted.property: 'yeah'

    multi_prop: { v: #123ABC q: 1000.xyz }
    comma_prop: { v: #123ABC, q: 1000, z: X.2 }
    multi_line_prop: {
        foo: 1.2.A.B
        bar: { 0: 1 },
    }

    bind: { <Return>: 'yeah' }

    nested_block {
        0: "digit identifier"
        one.two: "dotted identifier"
        bind: { <Button-1>: callback }
    }
}
'''


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
    # return Node and its API
    root = IGrammar(TKML_GRAMMAR).parse(SOURCE)
    assert isinstance(root, Node)
    assert root.full_text == SOURCE
    assert root.expr_name == 'tkml'
    assert root.end == len(SOURCE)

    # equivalence of tkml_tree and Node from .parse
    assert tkml_tree(SOURCE) == root

    # stop at Grammar
    grammar = IGrammar(TKML_GRAMMAR)
    assert isinstance(grammar, Grammar)

    # parse text by a specific rule
    source = '2701'
    node = grammar['number'].parse(source)
    assert node.full_text == source
    assert node.expr_name == 'number'
    assert node.end == len(source)

