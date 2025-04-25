"""
    | teleorithm |
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from parsimonious.nodes import Node
from parsimonious.grammar import Grammar
from parsimonious.exceptions import ParseError

from collections import OrderedDict

from tkml.grammar import TKML_GRAMMAR, IGrammar


class test_calling_parsimonious_Grammar(Spec):
    def setUp(self):
        self.valid_def = 'root = "23"'
        self.lousy_def = 'root ! "23"'

    def test_on_valid_grammar_definition_returns_Grammar(self):
        self.grammar = Grammar(self.valid_def)
        self.asrt(isinstance(self.grammar, Grammar))

    def test_on_lousy_grammar_definition_raises_ParseError(self):
        with self.rais(ParseError):
            self.grammar = Grammar(self.lousy_def)


class test_calling_parsimonious_Grammar_parse(Spec):
    def setUp(self):
        valid_def = 'root = "23"'
        self.grammar = Grammar(valid_def)
        self.valid_source = '23'
        self.lousy_source = 'absent'

    def test_on_valid_source_text_returns_Node(self):
        tree = self.grammar.parse(self.valid_source)
        self.asrt(isinstance(tree, Node))

    def test_on_lousy_source_text_raises_ParseError(self):
        with self.rais(ParseError):
            tree = self.grammar.parse(self.lousy_source)
    

class test_calling_IGrammar(Spec):
    def setUp(self):
        self.valid_def = 'root = "23"'
        self.lousy_def = 'root ! "23"'

    def test_with_valid_grammar_definition_returns_IGrammar(self):
        grammar = IGrammar(self.valid_def)
        self.asrt(isinstance(grammar, IGrammar))
        self.asrt(isinstance(grammar, Grammar))
        self.asrt(isinstance(grammar, OrderedDict))
        self.equa(
            list(grammar.keys()),
            ['root']
        )
        
    def test_with_lousy_grammar_definition_raises_ValueError(self):
        with self.rais(ValueError):
            grammar = IGrammar(self.lousy_def)
        

class test_calling_IGrammar_parse(Spec):
    def setUp(self):
        valid_def = 'root = "23"'
        self.grammar = IGrammar(valid_def)
        self.valid_source = '23'
        self.lousy_source = 'absent'

    def test_with_valid_source_text_returns_Node(self):
        tree = self.grammar.parse(self.valid_source)
        self.asrt(isinstance(tree, Node))
        self.equa(
            tree.full_text,
            self.valid_source
        )
        self.equa(
            tree.expr_name,
            'root'
        )
        self.equa(
            tree.end,
            len(self.valid_source)

        )

    def test_with_lousy_source_text_raises_ValueError(self):
        with self.rais(ValueError):
            node = self.grammar.parse(self.lousy_source)


if __name__ == '__main__':
    main(testRunner=Runner)

