# encoding: UTF-8
from tests.mock import Client
from tml.translation import Key
from tml.translation.missed import MissedKeys, MissedKeysLazy
import unittest
from tml import Application
from tml.language import Language


class missed_test(unittest.TestCase):
    def setUp(self):
        self.c = Client()
        self.c.read('applications/current', {'definition':1})
        self.c.read('languages/ru', {'definition':1})
        self.c.read('sources/register_keys', None)
        self.app = Application.load_default(self.c)
        self.lang = Language.load_by_locale(self.app, 'ru')

    def test_missed_key(self):
        m = MissedKeys(self.c)
        self.assertEquals({'status':'Ok'}, m.append(Key(language = self.lang, level = 2, label = 'Hello', description = 'greeting')))
        self.assertEquals('post', self.c.method, 'post request')
        self.assertEquals({'source_keys':'[{"keys": [{"locale": "ru", "level": 2, "description": "greeting", "label": "Hello"}]}]'}, self.c.params, 'Missed keys')

    def test_lazy_keys(self):
        m = MissedKeysLazy(self.c)
        self.c.url = None
        m.append(Key(language = self.lang, level = 2, label = 'Hello', description = 'greeting'))
        self.assertEquals(None, self.c.url, 'No requests after add')
        m.append(Key(language = self.lang, level = 2, label = 'Hello again', description = 'greeting'))
        m.submit_all()
        self.assertEquals('sources/register_keys', self.c.url, 'Post')
        self.assertEquals({'source_keys':'[{"keys": [{"locale": "ru", "level": 2, "description": "greeting", "label": "Hello"}, {"locale": "ru", "level": 2, "description": "greeting", "label": "Hello again"}]}]'}, self.c.params, 'Submit 2 keys')
        self.c.url = None
        m.submit_all()
        self.assertEquals(None, self.c.url, 'No not submit twice')


if __name__ == '__main__':
    unittest.main()