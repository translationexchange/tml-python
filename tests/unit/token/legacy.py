# encoding: UTF-8
import unittest
from tml.token.legacy import text_to_sprintf, suggest_label


class FakeLanguage(object):
    def __init__(self):
        self.contexts = self
        self.cases = {'dat': CaseMock()}

    def execute(self, rule, value):
        return rule

class ContextsMock(object):
    """ Stupid class to test context matching """
    @property
    def contexts(self):
        return self

    def execute(self, rules, data):
        return data.__class__.__name__

class CaseMock(object):
    def execute(self, data):
        return data.upper()


class TokenTest(unittest.TestCase):
    def test_legacy(self):
        format = text_to_sprintf(label, FakeLanguage())
        print expected
        print format
        self.assertEquals(expected, format, 'Check legacy')

    def test_suggest_label(self):
        self.assertEquals('Hello world', suggest_label('Hello world'), 'Suggest text')
        label = suggest_label('Hello %(name)s')
        self.assertEquals('Hello {name}', label, 'Suggest token')
        label = suggest_label('%(greeting)s %(name)s')
        self.assertEquals('{greeting} {name}', label, 'Suggest token')


if __name__ == '__main__':
    unittest.main()

