"""
    +-----+
    !kDoSE¡
    +-----+
    custom text
    for test and specs

"""
import re
from unittest import main, TestCase, TextTestRunner, TextTestResult


class Spec(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # mini-framework
        self.asrt = self.assertTrue
        self.equa = self.assertEqual
        self.rais = self.assertRaises
        self.subt = self.subTest


class Result(TextTestResult):
    def startTest(self, t):
        """
            output like ->
            __main__ Spec->BasicOntology something_matches_something
            __main__ TestBladderSystem test_1_fill_ball_with_oil
            __main__ TestBladderSystem test_2_drop_ball_filled_with_oil
            ...
        """
        super().startTest(t)

        pattern = r'<(\w+)\.(\w+) testMethod=(\w+)>'
        m = re.match(pattern, repr(t))
        mod, cls, meth = [m.string[slice(*m.span(i))] for i in (1, 2, 3)]

        if isinstance(t, Spec):
            cls = cls.replace('Test_', 'Spec->')
            cls = cls.replace('Test', 'Spec->')
            meth = meth.replace('test_', '')

        output = ' '.join((mod, cls, meth)) + '\n'
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

