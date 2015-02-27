# encoding: UTF-8
from tests.mock import Client
from tml.translation import Key
from tml.translation.context import Context
import unittest
from tml import Application
from tml.language import Language
from tml.rules.contexts.gender import Gender
from tml.rules.contexts import ValueIsNotMatchContext


class translation_test(unittest.TestCase):
    """ Test translations """
    def setUp(self):
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

    def test_context(self):
        c = Context({"count":{"number":"few"}})
        self.assertTrue(c.check({'count':3}, {}, self.lang), 'Test 3 is few')
        self.assertFalse(c.check({'count':1}, {}, self.lang), 'Test 1 is not few')
        # test multi context:
        c = Context({"count":{"number":"other"},"actor":{"gender":"male"}})
        self.assertTrue(c.check({'count':5, 'actor':Gender.male('Adam')}, {}, self.lang), 'many + male: OK')
        self.assertFalse(c.check({'count':5, 'actor':Gender.female('Eve')}, {}, self.lang), 'many + female: WRONG')
        # test invalid value:
        with self.assertRaises(ValueIsNotMatchContext) as context:
            self.assertFalse(c.check({'count':5, 'actor': 'Eve'}, {}, self.lang), 'many + female: WRONG')
        # test empty:
        c = Context({})
        self.assertTrue(c.check({'count':100}, {}, self.lang), 'Empty context - right anyway')


if  __name__ == '__main__':
    unittest.main()

