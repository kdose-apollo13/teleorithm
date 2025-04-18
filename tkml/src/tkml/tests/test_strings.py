"""
    | teleorithm |
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from parsimonious.nodes import Node
from parsimonious.grammar import Grammar

from textwrap import dedent

from tkml.grammar import tkml_tree, grammify, TKML_GRAMMAR, parse
from tkml.component import comb_for_components, TKMLFilter
from tkml.strings import valid_strings

from tkml.utils import node_iter, count_nodes


class test_valid_strings_as_properties(Spec):
    def setUp(self):
        self.grammar = grammify(TKML_GRAMMAR)
        self.sources = [f'Name {{ prop: {s} }}' for s in valid_strings]

    def test_parse_into_Nodes(self):
        for s in self.sources:
            tree = parse(s, self.grammar)
            self.asrt(isinstance(tree, Node))

    def test_Node_text_contains_string(self):
        """ string match is implicit in full text match """
        for s in self.sources:
            tree = parse(s, self.grammar)
            self.equa(tree.text, s)
            
    def test_source_contains_actual_string(self):
        for s in self.sources:
            tree = parse(s, self.grammar)
            for n in node_iter(tree):
                if n.expr_name == 'string':
                    self.asrt(n.text in s)

    def test_parsed_tree_has_23_nodes(self):
        for s in self.sources:
            tree = parse(s, self.grammar)
            node_qty = count_nodes(tree)
            self.equa(node_qty, 23)

if __name__ == '__main__':
    main(testRunner=Runner)


