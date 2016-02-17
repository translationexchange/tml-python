from __future__ import absolute_import
# encoding: UTF-8
from tests.mock import Client
from tml.api.pagination import allpages
import unittest
from tml import Application
from tml.language import Language
from tml.translation import Key
from tml.dictionary.language import LanguageDictionary
from tml.rules.contexts.gender import Gender
from tests.mock.fallback import Fallback
from tml.strings import to_string

class LanguageTest(unittest.TestCase):
    """ Test loading tranlations over API """
    def setUp(self):
        self.client = Client()
        self.client.read('languages/ru/definition', None)
        self.client.read('projects/current', None)
        self.client.read('projects/1/translations', {'locale':'ru', 'page': 1})
        self.app = Application.load_default(self.client)
        self.lang = Language.load_by_locale(self.app, 'ru')


    def test_translate(self):
        f = Fallback()
        dict = LanguageDictionary(self.lang, f)
        k = Key(label = '{actor} give you {count}',
                              description = 'somebody give you few apples',
                              language = self.lang)
        t = dict.get_translation(Key(label = '{actor} give you {count}',
                              description = 'somebody give you few apples',
                              language = self.lang))
        self.assertEquals(0, len(f.missed_keys),'No missing keys')
        self.assertEquals(3, len(t.options), 'All options loaded')
        self.assertEquals(to_string('Маша любезно дала тебе 2 яблока'), t.execute({'actor':Gender.female('Маша'),'count':2}, {}), 'Female few')

    def test_default(self):
        f = Fallback()
        dict = LanguageDictionary(self.lang, f)
        label = 'No translation'
        key = Key(label = label, language = self.lang)
        t = dict.get_translation(key)
        self.assertEquals(1, len(f.missed_keys), 'Key marked as missed')
        self.assertEquals(key, f.missed_keys[0], 'Key added to missed')
        self.assertEquals(label, t.execute({}, {}), 'Use default translation (fallback)')


if __name__ == '__main__':
    unittest.main()


