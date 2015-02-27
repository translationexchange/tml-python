# encoding: UTF-8
from tests.mock import Client
from tml.translation import Key
import unittest
from tml import Application
from tml.language import Language


class translation_test(unittest.TestCase):

    def setUp(self):
        print 'Hello'
        self.client = Client()
        self.client.read('applications/current')
        self.client.read('languages/ru')
        self.app = Application.load_default(self.client)
        self.lang = Language.load_by_locale(self.app, 'ru')

    def test_key(self):
        k = Key(label = '{name} give you {count} apples', description = 'apple', language= self.lang)
        self.assertEquals('{name} give you {count} apples', k.label, 'label')
        self.assertEquals('apple', k.description, 'description')
        self.assertEquals(self.lang.locale, k.language.locale, 'language')


    def test_key_hash(self):
        """ Test translation key """
        self.assertEquals('5174f88691edb354a9f46af6e7455bb8', Key(label = 'Test', language = self.lang).key, 'Key without description')
        self.assertEquals('2c868dcba5cd6e9f06dc77397b5a77b1', Key(label = '{name} give you {count} apples', description = 'apple', language= Language).key, 'Key with description')

if  __name__ == '__main__':
    unittest.main()

