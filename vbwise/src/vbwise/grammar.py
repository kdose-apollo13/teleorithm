from parsimonious.grammar import Grammar
from parsimonious.exceptions import ParseError
from parsimonious.nodes import Node


# TODO: analyze for associativity problems
# TODO: encompass unicode?
GNML_GRAMMAR = r'''
file = ws (node_def ws)*
node_def = node_start sp id_line sp content_lines sp node_end
node_start = "### NODE" sp newline
id_line = "---" sp "id" sp ":" sp complex_identifier sp newline
node_end = "### ENDNODE" sp newline
content_lines = content_line*
content_line = meta_line / tags_line / next_line / prev_line / text_line / code_line
meta_line = "---" sp "meta" sp ":" sp key_value_list* sp newline
tags_line = "---" sp "tags" sp ":" sp identifier_list* sp newline
next_line = "---" sp "next" sp ":" sp complex_identifier_list* sp newline
prev_line = "---" sp "prev" sp ":" sp complex_identifier_list* sp newline

text_line = text_level ">" sp text_content sp newline
text_level = "T" ~r"[1-3]"
text_content = ~r"[^\n]*"

code_line = code_level ">" sp code_content sp newline
code_level = "C" ~r"[1-3]"
code_content = ~r"[^\n]*"

identifier_list = identifier (sp "," sp identifier)*
key_value_list = key_value (sp "," sp key_value)*
key_value = identifier sp "=" sp identifier
complex_identifier_list = complex_identifier (sp "," sp complex_identifier)*
complex_identifier = identifier ( "." identifier )*
identifier = ~r"[a-zA-Z0-9_]+"
ws = ~r"[\r\n\t ]*"
sp = ~r"[ \t]*"
newline = "\n"
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
            pos = e.pos
            ctx = text[max(0, pos-20):pos+20]
            raise ValueError(f'invalid spec at {pos}. Context: ...{ctx}...')
        else:
            return tree


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
    sample = '''
### NODE
--- id: first.node.id
--- meta: key1=value1, key2=value2
--- tags: tag1, tag2, another_tag
T3> a truth
T1> fukyah
T3> between two lies
--- next: second_node.part1, third.node
--- prev: previous.node
### ENDNODE

### NODE
--- id: second_node
--- tags: single_tag
--- meta:
--- next:
--- prev: first.node.id
### ENDNODE

### NODE
--- id: third.node.with.more.parts
T1> some text line of level 1
T2> another line of level 2..
T3> a line of level 3
T1> lines can be toggled in some editor by flags eg v111 means all shown
--- next:
--- prev:
### ENDNODE

### NODE
--- id: third.node.with.more.parts
T1> def less(big_list, n=100):
T1>     z = zip(* [iter(big_list)] * n )
T1>     for t in z:
T1>         print(*t, sep='\\n')
T1>         if input() == 'q':
T1>             break
--- next:
--- prev:
### ENDNODE
'''
    try:
        parse_tree = IGrammar(GNML_GRAMMAR).parse(sample)
        assert isinstance(parse_tree, Node)
        print(parse_tree)
    except ValueError as e:
        print("Parse failed:", e)

