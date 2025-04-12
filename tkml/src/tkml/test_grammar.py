"""
    | teleorithm |
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from parsimonious.nodes import Node
from parsimonious.grammar import Grammar

from textwrap import dedent

from tkml.grammar import TKML_GRAMMAR, grammify, parse, tkml_tree
from tkml.utils import count_nodes


class test_TKML_grammar_string_when_grammified(Spec):
    def setUp(self):
        self.s = TKML_GRAMMAR

    def test_returns_Grammar(self):
        self.asrt(isinstance(self.s, str))
        # 
        g = grammify(self.s)
        # 
        self.asrt(isinstance(g, Grammar))


class test_empty_grammar_string_when_grammified(Spec):
    def setUp(self):
        self.s = ''

    def test_returns_Grammar(self):
        g = grammify(self.s)
        self.asrt(isinstance(g, Grammar))
        

class test_trivial_grammar_string_when_grammified(Spec):
    def setUp(self):
        self.s = 'root = "static"'

    def test_returns_Grammar(self):
        g = grammify(self.s)
        self.asrt(isinstance(g, Grammar))


# TODO: keep going with this, actual unicode
class test_unicode_range_string_when_grammified(Spec):
    def setUp(self):
        self.s = dedent(r'''
        root = text ws "!"
        text = ~"[\u4E00-\u9FFF]+"
        ws = ~"\\s*"
        ''')

    def test_returns_Grammar(self):
        g = grammify(self.s)
        self.asrt(isinstance(g, Grammar))


class test_trivial_source_string_and_grammar_when_parsed(Spec):
    def setUp(self):
        gstring = 'root = "static"'
        self.grammar = grammify(gstring)
        self.source = 'static'

    def test_returns_Node(self):
        n = parse(self.source, self.grammar)
        self.asrt(isinstance(n, Node))

    def test_Node_text_matches_source(self):
        n = parse(self.source, self.grammar)
        self.equa(n.text, self.source)

    def test_interpret_depth_first_traversal_of_Node_as_tree(self):
        def dfs(root):
            stack = list()
            stack.append(root)
            found = []
            
            while len(stack) > 0:
                node = stack.pop()
                stack.extend(c for c in node.children if c not in found)
                yield node.text

        tree = dfs(parse(self.source, self.grammar))
        # print(*list(tree), sep='\n')

        # TODO: how to test if tree?
        self.asrt(True)


class test_bad_tkml(Spec):
    """
        TODO: identify specific error and location in source for helpful debug msgs
    """
    def setUp(self):
        self.s = 'Name [ prop: wrong_braces ]'

    def test_raises_ValueError_on_unparseable_source(self):
        with self.rais(ValueError):
            tree = tkml_tree(self.s)


class test_empty_block_without_whitespace(Spec):
    def setUp(self):
        self.s = 'Name{}'

    def test_parses_into_Node_tree(self):
        tree = tkml_tree(self.s)
        self.asrt(isinstance(tree, Node))

    def test_tree_has_11_nodes(self):
        tree = tkml_tree(self.s)
        self.equa(count_nodes(tree), 11)


class test_empty_block_with_whitespace(Spec):
    def setUp(self):
        self.s = '   Name {   }     '

    def test_parses_into_Node_tree(self):
        tree = tkml_tree(self.s)
        self.asrt(isinstance(tree, Node))

    def test_tree_has_11_nodes(self):
        tree = tkml_tree(self.s)
        self.equa(count_nodes(tree), 11)

class test_block_with_and_without_whitespace(Spec):
    def setUp(self):
        self.spacious = ' Name {  } '
        self.compact = 'Name{}'

    def test_have_same_node_quantity(self):
        self.equa(
            count_nodes(tkml_tree(self.spacious)),
            count_nodes(tkml_tree(self.compact))
        )


if __name__ == '__main__':
    main(testRunner=Runner)

