from unittest import main, TestCase
from klab.ututils import Spec, Runner

import tomllib


def style_file_to_dict(name):
    """
        name
            : str
            : toml

        returns
            -> dict
    """
    with open(name, 'rb') as r:
        d = tomllib.load(r)

    return d

if __name__ == '__main__':
    from pprint import pprint
    d = style_file_to_dict('leafstyle.toml')
    pprint(d)

