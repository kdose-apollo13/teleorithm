"""
    | teleorithm |
    
    get loose get rhythm
    wonderful test style
"""
from unittest import main, TestCase
from klab.ututils import Spec, Runner

from tkml.utils import overwrite_dict


class test_overwrite_S_with_T_where_values_nondict(Spec):
    
    def test_updates_S_with_new_values(self):
        S = dict(a=1, b=2, c=3     )
        T = dict(     b=6, c=7, d=8)
        r = overwrite_dict(S, T)
        self.equa(
            r,
            dict(a=1, b=6, c=7, d=8)
        )

    def test_updates_S_with_new_values_2(self):
        S = dict(a=1, b=2, c=3, d=4)
        T = dict(     b=6, c=7     )
        r = overwrite_dict(S, T)
        self.equa(
            r,
            dict(a=1, b=6, c=7, d=4)
        )
        
    def test_updates_S_with_new_values_3(self):
        S = dict(     b=2, c=3     )
        T = dict(a=5, b=6, c=7, d=8)
        r = overwrite_dict(S, T)
        self.equa(
            r,
            dict(a=5, b=6, c=7, d=8)
        )

    def test_updates_S_with_new_values_4(self):
        S = dict(a=1, b=2, c=3, d=4)
        T = dict(a=5, b=6, c=7, d=8)
        r = overwrite_dict(S, T)
        self.equa(
            r,
            dict(a=5, b=6, c=7, d=8)
        )


class test_overwrite_S_with_T_where_values_dict(Spec):

    def test_updates_S_with_new_values(self):
        S = {'a': {'aa': 1, 'bb': 2}, 'b': {'cc': 3, 'dd': 4}}
        T = {'a': {'aa': 5         }, 'b': {         'dd': 8}}
        r = overwrite_dict(S, T)
        self.equa(
            r,
            {'a': {'aa': 5, 'bb': 2}, 'b': {'cc': 3, 'dd': 8}}
        )

    def test_updates_S_with_new_values_2(self):
        S = {'a': {'aa': 1, 'bb': 2}, 'b': {'cc': 3, 'dd': 4}}
        T = {'a': {'aa': 5, 'bb': 6}, 'b': {'cc': 7, 'dd': 8}}
        r = overwrite_dict(S, T)
        self.equa(
            r,
            {'a': {'aa': 5, 'bb': 6}, 'b': {'cc': 7, 'dd': 8}}
        )

    def test_updates_S_with_new_values_3(self):
        S = {'a': {         'bb': 2}, 'b': {         'dd': 4}}
        T = {'a': {'aa': 5, 'bb': 6}, 'b': {'cc': 7,        }}
        r = overwrite_dict(S, T)
        self.equa(
            r,
            {'a': {'aa': 5, 'bb': 6}, 'b': {'cc': 7, 'dd': 4}}
        )


if __name__ == '__main__':
    main(testRunner=Runner)

