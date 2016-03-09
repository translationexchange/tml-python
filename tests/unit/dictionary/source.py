from __future__ import absolute_import
# encoding: UTF-8
from tests.mock import Client
from tml.api.pagination import allpages
import unittest
from tml import Application
from tml.language import Language
from tml.translation import Key
from tml.dictionary.source import SourceDictionary
from tml.rules.contexts.gender import Gender
from tests.mock.fallback import Fallback
from json import dumps, loads
from tml.strings import to_string


class SourceTest(unittest.TestCase):
    """ Test loading tranlations over API """
    def setUp(self):
        self.client = Client.read_all()
        self.client.reloaded = []
        self.app = Application.load_default(self.client)
        self.lang = Language.load_by_locale(self.app, 'ru')

    def test_translate(self):
        f = Fallback()
        dict = SourceDictionary(language = self.lang, source = 'index')
        t = dict.get_translation(Key(label = '{actor} give you {count}',
                              description = 'somebody give you few apples',
                              language = self.lang))
        self.assertEquals(3, len(t.options), 'All options loaded')
        self.assertEquals(to_string('Маша любезно дала тебе 2 яблока'), t.execute({'actor':Gender.female('Маша'),'count':2}, {}), 'Female few')

    def test_default(self):
        dict = SourceDictionary(language = self.lang, source = 'index')
        label = 'No translation'
        key = Key(label = label, language = self.lang, level = 2)
        t = dict.get_translation(key)
        self.assertEquals(label, t.execute({}, {}), 'Use default tranlation')

if __name__ == '__main__':
    unittest.main()

