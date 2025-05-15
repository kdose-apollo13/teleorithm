"""
    | teleorithm |
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner


class test_curly_braces_within_an_f_string(Spec):
    def setUp(self):
        self.thing = 'whatever'
    
    def test_are_preserved_by_doubling_the_brace_chars(self):
        s = f'outer braces {{ all the {self.thing} forever and ever }}'
        self.equa(
            s,
            'outer braces { all the whatever forever and ever }'
        )
        

if __name__ == '__main__':
    main(testRunner=Runner)

