"""
    | teleorithm |
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from textwrap import dedent

from vbwise.gnmlgrammar import gnml_tree
from vbwise.gnmlvisitor import GNMLVisitor


class test_empty_node_when_walked_from_components(Spec):
    def setUp(self):
        source = dedent('''
            ### NODE
            --- id: some_id
            ### ENDNODE
        ''')
        self.tree = gnml_tree(source)

    def test_returns_list(self):
        root = GNMLVisitor().visit(self.tree)
        self.asrt(isinstance(root, list))
        
        self.equa(
            root,
            [
                {
                    'id': 'some_id',
                    'meta': {},
                    'tags': [],
                    'next': [],
                    'prev': [],
                    'code_lines': [],
                    'text_lines': []
                },
            ]
        )


class test_some_example_node(Spec):
    def setUp(self):
        source = dedent('''
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
        ''')
        self.tree = gnml_tree(source)

    def test_returns_list(self):
        root = GNMLVisitor().visit(self.tree)
        self.asrt(isinstance(root, list))

        self.equa(
            root,
            [
                {
                    'id': 'first.branch.22',
                    'meta': {'key1': 'value1', 'key2': 'value2'},
                    'tags': ['tag1', 'tag2', 'tag3'],
                    'next': ['first.branch.22', 'first.branch2.1'],
                    'prev': ['first.branch.20'],
                    'code_lines': [],
                    'text_lines': [
                        {'content': 'a truth', 'level': 'T3'},
                        {'content': 'fukyah', 'level': 'T1'},
                        {'content': 'between two lies', 'level': 'T3'}
                    ]
                },
            ]
        )


if __name__ == '__main__':
    main(testRunner=Runner)

