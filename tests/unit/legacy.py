# encoding: UTF-8
import unittest
from tml.legacy import text_to_sprintf, suggest_label, translate
from tml import Context
from tests.mock import Client
from tml.language import Language
from tml.application import Application
from tml.dictionary import Hashtable
from tml.dictionary.language import LanguageDictionary

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
        label = '{name||дал,дала,дал(а)} {to::dat} {count} {count|one:яблоко,few:яблока,many:яблок}'
        expected = u'%(name)s дал(а) %(to)s %(count)s яблок'
        format = text_to_sprintf(label, FakeLanguage())
        self.assertEquals(expected, format, 'Check legacy')

    def test_suggest_label(self):
        self.assertEquals('Hello world', suggest_label('Hello world'), 'Suggest text')
        label = suggest_label('Hello %(name)s')
        self.assertEquals('Hello {name}', label, 'Suggest token')
        label = suggest_label('%(greeting)s %(name)s')
        self.assertEquals('{greeting} {name}', label, 'Suggest token')

    def test_translate(self):
        """ Support legacy """
        c = Client.read_all()
        context = Context()
        context.language = Language.load_by_locale(Application.load_default(c), 'ru')
        context.dict = LanguageDictionary(context.language, [])
        self.assertEquals(u'Хелло Bill', translate(context, 'Hello %(name)s', {'name':'Bill'}, 'Greeting', {}))
        # Check old response syntax:
        context.dict.translations['8a7c891aa103e45e904a173f218cab9a'][0]['label'] = 'Привет %(name)s'
        self.assertEquals(u'Привет Bill', translate(context, 'Hello %(name)s', {'name':'Bill'}, 'Greeting', {}))

if __name__ == '__main__':
    unittest.main()

