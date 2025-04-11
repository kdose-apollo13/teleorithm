from unittest import main, TestCase
from klab.ututils import Spec, Runner

from parsimonious.nodes import Node
from parsimonious.grammar import Grammar

from textwrap import dedent

from tkml.grammar import TKML_GRAMMAR, grammify, parse


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
        

class test_minimal_grammar_string_when_grammified(Spec):
    def setUp(self):
        self.s = 'root = "static"'

    def test_returns_Grammar(self):
        g = grammify(self.s)
        self.asrt(isinstance(g, Grammar))


# TODO: keep going with this, actual unicode
class test_unicode_somewhere_string_when_grammified(Spec):
    def setUp(self):
        self.s = dedent(r'''
        root = text ws "!"
        text = ~"[\u4E00-\u9FFF]+"
        ws = ~"\\s*"
        ''')

    def test_returns_Grammar(self):
        g = grammify(self.s)
        self.asrt(isinstance(g, Grammar))


class test_source_string_and_grammar_when_parsed(Spec):
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


if __name__ == '__main__':
    main(testRunner=Runner)


