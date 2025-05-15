"""
    | teleorithm |
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from parsimonious.nodes import Node
from parsimonious.grammar import Grammar

from tkml.grammar import tkml_tree
from tkml.strings import valid_strings
from tkml.utils import node_iter, count_nodes


class test_valid_strings_as_properties(Spec):
    def setUp(self):
        self.sources = [f'Name {{ prop: {s} }}' for s in valid_strings]

    def test_parse_into_Nodes(self):
        for source in self.sources:
            tree = tkml_tree(source)
            self.asrt(isinstance(tree, Node))

    def test_Node_text_contains_string(self):
        """ string match is implicit in full text match """
        for source in self.sources:
            tree = tkml_tree(source)
            self.equa(tree.text, source)
            
    def test_source_contains_actual_string(self):
        for source in self.sources:
            tree = tkml_tree(source)
            for node in node_iter(tree):
                if node.expr_name == 'string':
                    self.asrt(node.text in source)

    def test_parsed_tree_has_23_nodes(self):
        for source in self.sources:
            tree = tkml_tree(source)
            node_qty = count_nodes(tree)
            self.equa(node_qty, 23)

if __name__ == '__main__':
    main(testRunner=Runner)


