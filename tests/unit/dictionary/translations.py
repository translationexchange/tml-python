# encoding: UTF-8
from tests.mock import Client
from tml.api.pagination import allpages
import unittest
from tml import Application
from tml.language import Language
from tml.translation import Key
from tml.dictionary.translations import Dictionary
from tml.rules.contexts.gender import Gender


class translations(unittest.TestCase):
    """ Test loading tranlations over API """
    def setUp(self):
        self.client = Client()
        self.client.read('translation_keys/8ad5a7fe0a12729764e31a1e3ca80059/translations', {'page':1, 'locale':'ru'}, 'translation_keys/8ad5a7fe0a12729764e31a1e3ca80059/translations_1.json')
        self.client.read('translation_keys/8ad5a7fe0a12729764e31a1e3ca80059/translations', {'page':2, 'locale':'ru'}, 'translation_keys/8ad5a7fe0a12729764e31a1e3ca80059/translations_2.json')
        self.client.read('languages/ru', {'definition': 1})
        self.client.read('applications/current', {'definition': 1})
        self.app = Application.load_default(self.client)
        self.lang = Language.load_by_locale(self.app, 'ru')


    def test_translate(self):
        missed_keys = []
        dict = Dictionary(missed_keys)
        t = dict.translate(Key(label = '{actor||give} you {count||apples}',
                              description = 'somebody give you few apples',
                              language = self.lang))
        self.assertEquals(0, len(missed_keys),'No missing keys')
        self.assertEquals(3, len(t.options), 'All options loaded')
        self.assertEquals('Маша любезно дала тебе 2 яблока', t.execute({'actor':Gender.female('Маша'),'count':2}, {}), 'Female few')

    def test_default(self):
        missed_keys = []
        dict = Dictionary(missed_keys)
        label = 'No translation'
        key = Key(label = label, language = self.lang)
        t = dict.translate(key)
        self.assertEquals(1, len(missed_keys), 'Key marked as missed')
        self.assertEquals(key, missed_keys[0], 'Key added to missed')
        self.assertEquals(label, t.execute({}, {}), 'Use default tranlation')


if __name__ == '__main__':
    unittest.main()

