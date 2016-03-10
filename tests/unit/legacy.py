# encoding: UTF-8
from __future__ import absolute_import
import unittest
import pytest
from tml.legacy import text_to_sprintf, suggest_label, translate
from tml import build_context
from tests.mock import Client
from tml.language import Language
from tml.application import Application
from tml.dictionary import Hashtable
from tml.dictionary.language import LanguageDictionary
import six
from tml.strings import to_string
from ..common import FakeLanguage, ContextsMock, CaseMock


@pytest.mark.usefixtures("build_context")
class LegacyTest(unittest.TestCase):
    def test_legacy(self):
        label = '{name||дал,дала,дал(а)} {to::dat} {count} {count|one:яблоко,few:яблока,many:яблок}'
        expected = to_string('%(name)s дал(а) %(to)s %(count)s яблок')
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
        context = self.build_context(client=c)
        context.dict = LanguageDictionary(context.language, [])
        t = translate(context, 'Hello %(name)s', {'name':'Bill'}, 'Greeting', {})
        self.assertEquals(to_string('Хелло Bill'), t)
        # Check old response syntax:
        context.dict.translations['8a7c891aa103e45e904a173f218cab9a'][0]['label'] = 'Привет %(name)s'
        t = translate(context, 'Hello %(name)s', {'name':'Bill'}, 'Greeting', {})
        self.assertEquals(to_string('Привет Bill'), t)

if __name__ == '__main__':
    unittest.main()

