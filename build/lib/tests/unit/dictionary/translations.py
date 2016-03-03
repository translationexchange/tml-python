from __future__ import absolute_import
# encoding: UTF-8
from tests.mock import Client
from tml.api.pagination import allpages
import unittest
from tml import Application
from tml.language import Language
from tml.translation import Key
from tml.dictionary.translations import Dictionary
from tml.rules.contexts.gender import Gender
from tests.mock.fallback import Fallback
from tml.strings import to_string


class TranslationsTest(unittest.TestCase):
    """ Test loading tranlations over API """
    def setUp(self):
        self.client = Client.read_all()
        self.app = Application.load_default(self.client)
        self.lang = Language.load_by_locale(self.app, 'ru')
        self.client.read('translation_keys/%s/translations' % self.apples_key().key, {'page':1, 'locale':'ru'}, 'translation_keys/8ad5a7fe0a12729764e31a1e3ca80059/translations_1.json')
        self.client.read('translation_keys/%s/translations' % self.apples_key().key, {'page':2, 'locale':'ru'}, 'translation_keys/8ad5a7fe0a12729764e31a1e3ca80059/translations_2.json')
        self.client.read('projects/current', {'definition': 1})

    def apples_key(self):
        return Key(label = '{actor} give you {count} apples', description = 'apple', language = self.lang)

    def test_translate(self):
        pass
        # f = Fallback()
        # dict = Dictionary(f)
        # t = dict.get_translation(self.apples_key())
        # self.assertEquals(3, len(t.options), 'All options loaded')
        # self.assertEquals(0, len(f.missed_keys), 'No missed keys')
        # self.assertEquals(to_string('Маша любезно дала тебе 2 яблока'), t.execute({'actor':Gender.female('Маша'),'count':2}, {}), 'Female few')

    def test_default(self):
        f = Fallback()
        dict = Dictionary(f)
        label = 'No translation'
        key = Key(label = label, language = self.lang)
        t = dict.get_translation(key)
        self.assertEquals(1, len(f.missed_keys), 'Key marked as missed')
        self.assertEquals(key, f.missed_keys[0], 'Key added to missed')
        self.assertEquals(label, t.execute({}, {}), 'Use default tranlation')


if __name__ == '__main__':
    unittest.main()

