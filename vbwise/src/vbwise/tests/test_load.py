"""
    | teleorithm |
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from textwrap import dedent

from vbwise import load


class test_load_toml_string(Spec):
    def setUp(self):
        self.s = dedent('''
            # comment above key value pair
            'key1' = 'value1'

            [Table]
            'key2' = 'value2'

            [[Array]]
            'key3' = { 'key4' = 'value4' }
        ''')

    def test_returns_dict(self):
        d = load.toml_string(self.s)
        self.equa(
            d,
            {
                'key1': 'value1',
                'Table': {'key2': 'value2'},
                'Array': [
                    {'key3': {'key4': 'value4'}},
                ]
            }
        )


class test_load_tkml_string(Spec):
    def setUp(self):
        self.s = dedent('''
            App {
                Tk { title: 'whatever' geometry: '400x300' }
            }
        ''')

    def test_returns_dict(self):
        d = load.tkml_string(self.s)
        self.equa(
            d,
            {
                'type': 'App',
                'props': {},
                'parts': [
                    {
                        'type': 'Tk',
                        'props': {'geometry': '400x300', 'title': 'whatever'},
                        'parts': []
                    },
                ]
            }
        )


class test_load_gnml_string(Spec):
    def setUp(self):
        self.s = dedent('''
            ### NODE
            --- id: some_node
            --- meta: author = kDoSE, version = 1.2.3
            --- tags: 1, 2, 3, go
            T1> aim for the moon, destroy the stars
            ### ENDNODE
        ''')

    def test_returns_list(self):
        l = load.gnml_string(self.s)
        self.equa(
            l,
            [
                {
                    'id': 'some_node',
                    'meta': {'author': 'kDoSE', 'version': '1.2.3'},
                    'tags': ['1', '2', '3', 'go'],
                    'next': [],
                    'prev': [],
                    'text_lines': [
                        {
                            'level': 'T1',
                            'content': 'aim for the moon, destroy the stars',
                        }
                    ],
                    'code_lines': [],
                }
            ]
        )

class test_load_python_string(Spec):
    def setUp(self):
        self.s = dedent('''
            def some_func(x):
                y = x ** 2
                return y
        ''')

    def test_returns_dict(self):
        d = load.python_string(self.s)
        self.maxDiff = None
        self.asrt('some_func' in d)
        
        self.equa(
            d['some_func'](3),
            9
        )


if __name__ == '__main__':
    main(testRunner=Runner)

