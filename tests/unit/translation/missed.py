# encoding: UTF-8
from tests.mock import Client
from tml.translation import Key
from tml.translation.missed import MissedKey
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
        m = MissedKey(self.c)
        self.assertEquals({'status':'Ok'}, m.append(Key(language = self.lang, level = 2, label = 'Hello', description = 'greeting')))
        self.assertEquals('post', self.c.method, 'post request')
        self.assertEquals({'source_keys':'[{"keys": [{"locale": "ru", "level": 2, "description": "greeting", "label": "Hello"}]}]'}, self.c.params, 'Missed keys')


if __name__ == '__main__':
    unittest.main()