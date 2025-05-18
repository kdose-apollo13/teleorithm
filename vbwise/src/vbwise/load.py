"""
    | teleorithm |
"""
import json
import tomllib

from vbwise.tkmlgrammar import tkml_tree
from vbwise.tkmlvisitor import TKMLVisitor

from vbwise.gnmlgrammar import gnml_tree
from vbwise.gnmlvisitor import GNMLVisitor


def json_string(s):
    """
        s
            : str

        returns
            > dict
    """
    d = json.loads(s)
    return d


def json_file(path):
    """
        path
            : str

        returns
            > dict
    """
    with open(path, 'rt') as r:
        d = json.load(r)

    return d


def toml_string(s):
    """
        s
            : str

        returns
            > dict
    """
    d = tomllib.loads(s)
    return d


def toml_file(path):
    """
        path
            : str

        returns
            > dict
    """
    with open(path, 'rb') as r:
        d = tomllib.load(r)
    return d


def tkml_string(s):
    """
        s
            : str

        returns
            > dict
    """
    t = tkml_tree(s)
    d = TKMLVisitor().visit(t)
    return d


def tkml_file(path):
    """
        path
            : str

        returns
            > dict
    """
    with open(path, 'rt') as r:
        s = r.read()

    return tkml_string(s)


def gnml_string(s):
    """
        s
            : str

        returns
            > list
    """
    t = gnml_tree(s)
    l = GNMLVisitor().visit(t)
    return l


def gnml_file(path):
    """
        path
            : str

        returns
            > list
    """
    with open(path, 'rt') as r:
        s = r.read()

    return gnml_string(s)


def python_string(s):
    """
        s
            : str

        returns
            > dict
    """
    ns = {}
    exec(s, ns)
    return ns

