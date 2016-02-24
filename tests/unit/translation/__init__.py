# encoding: UTF-8
from __future__ import absolute_import
from tests.mock import Client
from tml.translation import Key, TranslationOption, OptionIsNotSupported,\
    Translation, OptionIsNotFound, generate_key
from tml.translation.context import Context
import unittest
from tml.application import Application
from tml.language import Language
from tml.rules.contexts.gender import Gender
from tml.rules.contexts import ValueIsNotMatchContext
from tml.exceptions import RequiredArgumentIsNotPassed
from json import loads
from tml.strings import to_string


class TranslationTest(unittest.TestCase):
    """ Test translations """
    def setUp(self):
        self.client = Client()
        self.client.read('projects/current/definition')
        self.client.read('languages/ru')
        self.app = Application.load_default(self.client)
        self.lang = Language.load_by_locale(self.app, 'ru')

    def test_key(self):
        k = Key(label = '{name} give you {count} apples', description = 'apple', language= self.lang, level = 5)
        self.assertEquals('{name} give you {count} apples', k.label, 'label')
        self.assertEquals('apple', k.description, 'description')
        self.assertEquals(self.lang.locale, k.language.locale, 'language')
        self.assertEquals({'locale':'ru', 'level':5,'description':'apple','label':'{name} give you {count} apples'}, k.as_dict, 'As dict function')
        self.assertEquals('1', k.build_key('1'), 'build key with key')
        self.assertEquals('2c868dcba5cd6e9f06dc77397b5a77b1', k.build_key(), 'generate key')

    def test_key_hash(self):
        """ Test translation key """
        self.assertEquals('5174f88691edb354a9f46af6e7455bb8', generate_key('Test'), 'without description')
        self.assertEquals('2c868dcba5cd6e9f06dc77397b5a77b1', generate_key('{name} give you {count} apples', description='apple'), 'with description')
        self.assertEquals('5174f88691edb354a9f46af6e7455bb8', Key(label='Test', language=self.lang).key, 'Key without description')
        self.assertEquals('2c868dcba5cd6e9f06dc77397b5a77b1', Key(label='{name} give you {count} apples', description='apple', language=self.lang).key, 'Key with description')
        self.assertEquals('f9048053ea53b494f948b88b334f7ad0', Key(label='Submit', description='Submit recipe', language=self.lang).key)

    def test_options(self):
        t = TranslationOption('{name||дал, дала, дало} {to::dat} {count} яблоко', self.lang, {'count':{'number':'one'}})
        self.assertEquals(to_string('Вася дал Маше 21 яблоко'), t.execute({'name': Gender.male('Вася'), 'to': Gender.female('Маша'), 'count': 21}, {}))
        self.assertEquals(to_string('Лена дала Льву 21 яблоко'), t.execute({'name': Gender.female('Лена'), 'to': Gender.male('Лев'), 'count': 21}, {}))
        with self.assertRaises(OptionIsNotSupported):
            t.execute({'name': Gender.male('John'),'count': 2}, {})
        with self.assertRaises(RequiredArgumentIsNotPassed):
            t.execute({}, {})
        with self.assertRaises(RequiredArgumentIsNotPassed):
            t.execute({'count': 1}, {})
        t = TranslationOption('Anyway', self.lang, {})
        self.assertEquals('Anyway', t.execute({}, {}), 'Anyway execute')

    def test_context(self):
        c = Context({"count":{"number":"few"}})
        self.assertTrue(c.check({'count':3}, {}, self.lang), 'Test 3 is few')
        self.assertFalse(c.check({'count':1}, {}, self.lang), 'Test 1 is not few')
        # test multi context:
        c = Context({"count":{"number":"other"},"actor":{"gender":"male"}})
        self.assertTrue(c.check({'count':5, 'actor': Gender.male('Adam')}, {}, self.lang), 'many + male: OK')
        self.assertFalse(c.check({'count':5, 'actor': Gender.female('Eve')}, {}, self.lang), 'many + female: WRONG')
        # test invalid value:
        with self.assertRaises(ValueIsNotMatchContext) as context:
            self.assertFalse(c.check({'count':5, 'actor': 'Eve'}, {}, self.lang), 'many + female: WRONG')
        # test empty:
        c = Context({})
        self.assertTrue(c.check({'count':100}, {}, self.lang), 'Empty context - right anyway')

    def test_tranlation(self):
        url = 'translation_keys/8ad5a7fe0a12729764e31a1e3ca80059/translations'
        self.client.read(url, {'locale':'ru'})
        key = Key(label = '{actor} give you {count} apples',
                  language = self.lang)
        t = Translation.from_data(key,
                                  self.client.get(url, params={'locale':'ru'})['results'])

        self.assertEquals(to_string('Маша любезно дала тебе 2 яблока'), t.execute({'actor':Gender.female('Маша'),'count':2}, {}), 'Female few')
        male_one = {'actor':{'gender':'male','name':'Вася'},'count':1}
        self.assertEquals(to_string('Вася дал тебе всего 1 яблоко, мужик!'),
                          t.execute(male_one, {}),
                          'Male one')
        self.assertEquals(to_string('{actor} дал тебе всего {count} яблоко, мужик!'),
                          t.fetch_option(male_one, {}).label,
                          'Check fetch')
        self.assertEquals(to_string('{actor||дал, дала, дало} тебе {count||one: яблоко, few: яблока, many: яблок}'),
                  t.fetch_option({}, {}).label,
                  'fetch default')
        self.assertEquals(to_string('Вася дал тебе 5 яблок'), t.execute({'actor':{'gender':'male','name':'Вася'},'count':5}, {}), 'Male many')
        t = Translation.from_data(key, [{'label': "{xxx||рум,румки,румок}"}])
        t = Translation.from_data(key, [{"label":"{to::dat}"}])
        sdata = '{"to":{"gender":"male","name":"Вася"}}'
        self.assertEquals(to_string("Васе"), t.execute(loads(sdata), {}), 'Васе')
        t = Translation(key, [])
        with self.assertRaises(OptionIsNotFound):
            t.execute({'actor':{'gender':'male','name':'John'},'count':5}, {})

if  __name__ == '__main__':
    unittest.main()

