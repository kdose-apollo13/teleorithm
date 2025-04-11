"""
    |teleorithm|

    in sublcass of TextTestResult -> method startTest accepts t
    repr(t) looks like this:

    <__main__.TestBladderSystem testMethod=test_1_fill_ball_with_oil>

    want this:

    __main__
        given some condition (or whatever)
        --> when we do this then something else

"""
import re
from textwrap import dedent
from unittest import main, TestCase, TextTestRunner, TextTestResult


def extract_names(s):
    """
        s
            : str
            : <__main__.TestOneTwo testMethod=test_three_four>

        returns
            -> tuple[str]
            -> module, class, method
            -> (eg) ('__main__', 'TestOneTwo', 'test_three_four')
    """
    pattern = r'<(\w+)\.(\w+) testMethod=(\w+)>'
    m = re.match(pattern, s)
    return m.groups()


def scrub(s):
    """
        s
            : str

        returns
            -> str
            -> leading 'Test' or 'test' removed from both class and method names
    """
    return re.sub('^[Tt]est_?', '', s)


def space(s):
    """
        s
            : str

        returns
            -> input s with underscores replaced by spaces '_' -> ' '
    """
    return re.sub('_', ' ', s)


class Spec(TestCase):
    def __init__(self, *args, **kwargs):
        """
            mini-framework -> consistent, simplified condition names        
        """
        super().__init__(*args, **kwargs)

        self.asrt = self.assertTrue
        self.equa = self.assertEqual
        self.rais = self.assertRaises
        self.subt = self.subTest


class Result(TextTestResult):
    def startTest(self, t):
        """
            t
                : type inheriting from TestCase

        """
        super().startTest(t)

        s = repr(t)
        names = extract_names(s)
        mod, cls, meth = (scrub(n) for n in names)
        cls, meth = (space(s) for s in (cls, meth))

        output = dedent(f'''\

        {mod}
            {cls}
            --> {meth}
        ''')

        self.stream.write(output)


class Runner(TextTestRunner):
    def _makeResult(self):
        # verbosity -> 0
        return Result(self.stream, self.descriptions, 0)


class TestInitialData(Spec):
    def test_to_FinalData(self):
        self.assertTrue(1)
        ...
        # OR
        self.asrt(1)
        self.equa(1, 1.0)
        with self.rais(ZeroDivisionError):
            1/0
        # TODO: example of using self.subt


class TestBladderSystem(TestCase):
    def test_1_fill_ball_with_oil(self):
        self.assertTrue(1)

    def test_2_drop_ball_filled_with_oil(self):
        self.assertTrue(1)


if __name__ == '__main__':
    main(testRunner=Runner)

