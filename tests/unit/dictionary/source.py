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


class translations(unittest.TestCase):
    """ Test loading tranlations over API """
    def setUp(self):
        self.client = Client.read_all()
        self.app = Application.load_default(self.client)
        self.lang = Language.load_by_locale(self.app, 'ru')

    def test_translate(self):
        f = Fallback()
        dict = SourceDictionary(language = self.lang, source = 'index')
        t = dict.translate(Key(label = '{actor} give you {count}',
                              description = 'somebody give you few apples',
                              language = self.lang))
        self.assertEquals(3, len(t.options), 'All options loaded')
        self.assertEquals('Маша любезно дала тебе 2 яблока', t.execute({'actor':Gender.female('Маша'),'count':2}, {}), 'Female few')

    def test_default(self):
        dict = SourceDictionary(language = self.lang, source = 'index')
        label = 'No translation'
        key = Key(label = label, language = self.lang, level = 2)
        t = dict.translate(key)
        self.assertEquals(label, t.execute({}, {}), 'Use default tranlation')
        del dict
        self.assertEquals('sources/register_keys', self.client.url, 'Post')
        submit_keys = [{"source":"index","keys": [{"locale": "ru", "level": 2, "description": "", "label": "No translation"}]}]
        self.assertEquals(submit_keys, loads(self.client.params['source_keys']), 'Submit keys')
        self.assertEquals(1, len(self.client.reloaded), 'Page reloaded')


if __name__ == '__main__':
    unittest.main()

