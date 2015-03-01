# encoding: UTF-8
from tests.mock import Client
from tml.translation import Key, TranslationOption, OptionIsNotSupported,\
    Translation
from tml.translation.context import Context
import unittest
from tml import Application
from tml.language import Language
from tml.rules.contexts.gender import Gender
from tml.rules.contexts import ValueIsNotMatchContext
from tml.exceptions import RequiredArgumentIsNotPassed


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

    def test_options(self):
        t = TranslationOption('{name||дал, дала, дало} тебе {count} яблоко', self.lang, {'count':{'number':'one'}})
        self.assertEquals('Вася дал тебе 21 яблоко', t.execute({'name': Gender.male('Вася'),'count': 21}, {}))
        self.assertEquals('Лена дала тебе 21 яблоко', t.execute({'name': Gender.female('Лена'),'count': 21}, {}))
        with self.assertRaises(OptionIsNotSupported):
            t.execute({'name': Gender.male('John'),'count': 2}, {})
        with self.assertRaises(RequiredArgumentIsNotPassed):
            t.execute({}, {})
        with self.assertRaises(RequiredArgumentIsNotPassed):
            t.execute({'count': 1}, {})
        t = TranslationOption('Anyway', self.lang, {})
        self.assertEquals('Anyway', t.execute({}, {}), 'Anyway execute')

    def test_tranlation(self):
        url = 'translation_keys/8ad5a7fe0a12729764e31a1e3ca80059/translations'
        self.client.read(url)
        key = Key(label = '{actor} give you {count} apples',
                  language = self.lang)
        t = Translation.from_data(key,
                                  self.client.get(url, {})['results'])
        self.assertEquals('Маша любезно дала тебе 2 яблока', t.execute({'actor':Gender.female('Маша'),'count':2}, {}), 'Female few')
        self.assertEquals('Вася дал тебе всего 1 яблоко, мужик!', t.execute({'actor':{'gender':'male','name':'Вася'},'count':1}, {}), 'Male one')
        self.assertEquals('Вася дал тебе 5 яблок', t.execute({'actor':{'gender':'male','name':'Вася'},'count':5}, {}), 'Male many')
        
        t = Translation(key, [])
        self.assertEquals('John give you 5 apples', t.execute({'actor':{'gender':'male','name':'John'},'count':5}, {}), 'Use label by default')

if  __name__ == '__main__':
    unittest.main()
