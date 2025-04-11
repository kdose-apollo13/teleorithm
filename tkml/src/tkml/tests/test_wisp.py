"""
    ------------
    test_wisp.py
    ------------

    tkml <-> dict <-> json <-> toml
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from textwrap import dedent
import tkinter as tk

from parsimonious.grammar import Grammar
from parsimonious.nodes import Node, NodeVisitor
from parsimonious.exceptions import ParseError

from wisp import tkml_grammar, parse_source, TKMLVisitor
from strings import valid_strings

from tkml_utils import node_iter, node_counter


class TestFStringContainingCurlyBraces(Spec):
    
    def test_doubling_the_braces_gives_correct_string(self):
        somebody = 'van damme'
        s = f'outer braces {{ this guy, {somebody}, is back in shape! }}'
        self.equa(
            s,
            'outer braces { this guy, van damme, is back in shape! }'
        )


class TestBadTKML(Spec):
    """
        TODO: identify specific error and location in source for helpful debug msgs
    """
    def setUp(self):
        self.grammar = tkml_grammar

    def test_raises_ValueError_on_unparseable_source(self):
        bad_source = '2Hello { this app is wrong }'
        with self.rais(ValueError):
            tree = parse_source(bad_source, self.grammar)


class TestEmptyBlock(Spec):
    """
        has nothing to do with tkinter yet - keep it generic
    """
    def setUp(self):
        self.grammar = tkml_grammar

    def test_parses_successfully_into_tree(self):
        source = 'Name {}'
        tree = parse_source(source, self.grammar)
        self.asrt(isinstance(tree, Node))
    
    def test_parsed_tree_text_matches_source(self):
        source = 'Name {}'
        tree = parse_source(source, self.grammar)
        self.equa(tree.text, source)

    def test_parsed_tree_has_11_nodes(self):
        source = 'Name {}'
        tree = parse_source(source, self.grammar)

        node_qty = sum(node_counter(tree))
        self.equa(node_qty, 11)

        tree_text = tree.prettily()
        line_qty = len(tree_text.splitlines())
        self.equa(line_qty, 11)
        
    def test_single_and_multiline_sources_have_identical_trees(self):
        single = 'Name {}'

        multi = dedent('''\
        Name {}''')

        tree_single = parse_source(single, self.grammar)
        tree_multi = parse_source(multi, self.grammar)
        self.equa(tree_single, tree_multi)

    def test_whitespace_is_preserved(self):
        source = ' Name   {   }   '
        tree = parse_source(source, self.grammar)
        self.equa(tree.text, source)

    def test_whitespace_modifies_tree_somehow(self):
        compact = 'Name{}'
        spaced = ' Name   {   }   '

        tree_compact = parse_source(compact, self.grammar)
        tree_spaced = parse_source(spaced, self.grammar)
        self.asrt(tree_compact != tree_spaced)

    def test_whitespace_does_not_change_node_quantity(self):
        compact = 'Name{}'
        spaced = ' Name   {   }   '

        tree_compact = parse_source(compact, self.grammar)
        tree_spaced = parse_source(spaced, self.grammar)

        compact_qty = sum(node_counter(tree_compact))
        spaced_qty = sum(node_counter(tree_spaced))
        self.equa(compact_qty, spaced_qty)


class TestBlockWithOneValueProperty(Spec):
    def setUp(self):
        self.grammar = tkml_grammar
        self.source = dedent('''\
        Name {
            prop: 23
        }
        ''')
        
    def test_parses_successfully_into_tree(self):
        tree = parse_source(self.source, self.grammar)
        self.asrt(isinstance(tree, Node))

    def test_parsed_tree_text_matches_source(self):
        tree = parse_source(self.source, self.grammar)
        self.equa(tree.text, self.source)

    def test_parsed_tree_has_21_nodes(self):
        tree = parse_source(self.source, self.grammar)
        node_qty = sum(node_counter(tree))
        self.equa(node_qty, 21)



if __name__ == '__main__':
    main(testRunner=Runner)


