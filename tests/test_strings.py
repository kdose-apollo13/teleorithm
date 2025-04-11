""" 
    ---------------
    test_strings.py
    ---------------
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from parsimonious.nodes import Node
from parsimonious.grammar import Grammar

from wisp import tkml_grammar, parse_source
from strings import valid_strings

from tkml_utils import node_iter, node_counter


class TestBlockWithOneStringProperty(Spec):
    def setUp(self):
        self.grammar = tkml_grammar
        self.sources = [f'Name {{ prop: {s} }}' for s in valid_strings]
        
    def test_parses_successfully_into_tree(self):
        for source in self.sources:
            self.asrt(isinstance(self.grammar, Grammar))
            self.asrt(isinstance(source, str))
            tree = parse_source(source, self.grammar)
            self.asrt(isinstance(tree, Node))

    def test_parsed_tree_text_matches_source(self):
        """ string match is implicit in full text match """
        for source in self.sources:
            tree = parse_source(source, self.grammar)
            self.equa(tree.text, source)

    def test_parsed_tree_string_node_text_in_source(self):
        for source in self.sources:
            tree = parse_source(source, self.grammar)
            for n in node_iter(tree):
                if n.expr_name == 'string':
                    t = n.text
                    self.asrt(t in source)

    def test_parsed_tree_has_22_nodes(self):
        for source in self.sources:
            tree = parse_source(source, self.grammar)
            node_qty = sum(node_counter(tree))
            self.equa(node_qty, 22)


if __name__ == '__main__':
    main(testRunner=Runner)

