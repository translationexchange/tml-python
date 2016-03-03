# encoding: UTF-8
from __future__ import absolute_import
from tests.mock import Client
from tml.translation import Key
from tml.translation.missed import MissedKeys
import unittest
from json import dumps, loads
from tml import Application
from tml.language import Language


class MissedTest(unittest.TestCase):
    def setUp(self):
        self.c = Client()
        self.c.read('projects/current', None)
        self.c.read('languages/ru', None)
        self.c.read('sources/register_keys', None)
        self.app = Application.load_default(self.c)
        self.lang = Language.load_by_locale(self.app, 'ru')

    def test_lazy_keys(self):
        m = MissedKeys(self.c)
        self.c.url = None
        m.append(Key(language = self.lang, level = 2, label = 'Hello', description = 'greeting'))
        self.assertEquals(None, self.c.url, 'No requests after add')
        m.append(Key(language = self.lang, level = 2, label = 'Hello again', description = 'greeting'))
        m.submit_all()
        self.assertEquals('sources/register_keys', self.c.url, 'Post')
        expected = [{"keys": [{"locale": "ru", "level": 2, "description": "greeting", "label": "Hello"},{"locale": "ru", "level": 2, "description": "greeting", "label": "Hello again"}]}]
        submited_keys = loads(self.c.params['source_keys'])
        self.assertEquals(len(expected[0]['keys']), len(submited_keys[0]['keys']), 'Submit 2 keys')
        self.c.url = None
        m.submit_all()
        self.assertEquals(None, self.c.url, 'No not submit twice')


if __name__ == '__main__':
    unittest.main()
