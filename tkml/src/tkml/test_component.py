"""
    | teleorithm |
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from parsimonious.nodes import Node
from parsimonious.grammar import Grammar

from textwrap import dedent

from tkml.grammar import tkml_tree
from tkml.component import comb_for_components, TKMLFilter
from tkml.utils import count_nodes


class test_curly_braces_within_an_f_string(Spec):
    def setUp(self):
        self.thing = 'whatever'
    
    def test_are_preserved_by_doubling_the_brace_chars(self):
        s = f'outer braces {{ all the {self.thing} forever and ever }}'
        self.equa(
            s,
            'outer braces { all the whatever forever and ever }'
        )

class test_single_and_multiline_sources(Spec):
    def setUp(self):
        self.single = 'Name {}'

        self.multi = dedent('''\
        Name {}''')

    def test_have_identical_trees(self):
        tree_single = tkml_tree(self.single)
        tree_multi = tkml_tree(self.multi)
        self.equa(tree_single, tree_multi)
        

class test_grammar_tree_when_combed_with_NodeFilter(Spec):
    def setUp(self):
        self.tree = tkml_tree('Name {}')
        self.node_filter = TKMLFilter()
    
    def test_return_dict(self):
        d = comb_for_components(self.tree, self.node_filter)
        self.asrt(isinstance(d, dict))

    def test_interpret_dict_as_components(self):
        comps = comb_for_components(self.tree, self.node_filter)
        self.equa(
            comps,
            {
                'type': 'Name',
                'props': {},
                'children': []
            }
        )


if __name__ == '__main__':
    main(testRunner=Runner)


