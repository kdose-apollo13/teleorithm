"""
    | teleorithm |

    Grafnav Markup Language
"""
from parsimonious.grammar import Grammar
from parsimonious.nodes import Node

from vbwise.igrammar import IGrammar


GNML_GRAMMAR = r'''
    gnml                = ws (node_def ws)*
    node_def            = node_start sp id_line sp content_lines sp node_end
    node_start          = "### NODE" sp newline
    id_line             = "---" sp "id" sp ":" sp complex_identifier sp newline
    node_end            = "### ENDNODE" sp newline
    content_lines       = content_line*
    content_line        = meta_line / tags_line / next_line / prev_line / text_line / code_line
    meta_line           = "---" sp "meta" sp ":" sp key_value_list* sp newline
    tags_line           = "---" sp "tags" sp ":" sp identifier_list* sp newline
    next_line           = "---" sp "next" sp ":" sp complex_identifier_list* sp newline
    prev_line           = "---" sp "prev" sp ":" sp complex_identifier_list* sp newline

    text_line           = text_level ">" sp text_content sp newline
    text_level          = "T" ~r"[1-3]"
    text_content        = ~r"[^\n]*"

    code_line           = code_level ">" sp code_content sp newline
    code_level          = "C" ~r"[1-3]"
    code_content        = ~r"[^\n]*"

    identifier_list             = identifier (sp "," sp identifier)*
    key_value_list              = key_value (sp "," sp key_value)*
    key_value                   = identifier sp "=" sp complex_identifier
    complex_identifier_list     = complex_identifier (sp "," sp complex_identifier)*
    complex_identifier          = identifier ( "." identifier )*

    identifier      = ~r"[a-zA-Z0-9_]+"
    ws              = ~r"[\r\n\t ]*"
    sp              = ~r"[ \t]*"
    newline         = "\n"
'''

EXAMPLE_SOURCE = '''
### NODE
--- id: first.branch.22
--- meta: key1=value1, key2=value2
--- tags: tag1, tag2, tag3
T3> a truth
T1> fukyah
T3> between two lies
--- next: first.branch.22, first.branch2.1
--- prev: first.branch.20
### ENDNODE

### NODE
--- id: some_node
--- tags: single_tag
--- meta: version=0.2.3, author=kDoSE
--- next:
--- prev: 
C1> def some_func(x):
C1>     return x**2
C1> 
### ENDNODE
'''


def gnml_tree(source):
    """
        source
            : str
            : gnml-compliant source text

        returns
            > parsimonious.nodes.Node

        raises
            ! ValueError

    """
    tree = IGrammar(GNML_GRAMMAR).parse(source)
    return tree


if __name__ == '__main__':
    root = IGrammar(GNML_GRAMMAR).parse(EXAMPLE_SOURCE)
    assert isinstance(root, Node)
    assert root.full_text == EXAMPLE_SOURCE
    assert root.expr_name == 'gnml'
    assert root.end == len(EXAMPLE_SOURCE)

    assert gnml_tree(EXAMPLE_SOURCE) == root

    grammar = IGrammar(GNML_GRAMMAR)
    assert isinstance(grammar, Grammar)

    source = 'first.second.third, yeah, yeah.again,nospace99'
    node = grammar['complex_identifier_list'].parse(source)
    assert node.full_text == source
    assert node.expr_name == 'complex_identifier_list'
    assert node.end == len(source)

