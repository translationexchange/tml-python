from __future__ import absolute_import
# encoding: UTF-8
import unittest
from tml.application import Application, LanguageNotSupported
from tml.language import Language
from tml.source import SourceTranslations
from tml.dictionary.source import SourceDictionary
from tests.mock import Client

LANGUAGES = [
    {'id': 233, 'locale':'ru', 'native_name': 'Русский', 'right_to_left': False},
    {'id': 2, 'locale':'en', 'native_name': 'English', 'right_to_left': False}]

class ApplicationTest(unittest.TestCase):

    def setUp(self):
        self.client = Client.read_all()

    def test_instance(self):
        app = Application.from_dict(self.client, {'id':100, 'languages': LANGUAGES, 'default_locale':'en'})
        self.assertEquals(100, app.id, 'id getter')
        self.assertEquals([Language.from_dict(app, l) for l in LANGUAGES], app.languages, 'compare languages')
        self.assertEquals('en', app.default_locale, 'Default locale')

    def test_language(self):
        app = Application(self.client, 100, LANGUAGES, 'en')
        self.assertEquals('languages/ru', app.get_language_url('ru'), 'URL for ru')
        self.assertEquals('languages/en', app.get_language_url('en'), 'URL for en')
        with self.assertRaises(LanguageNotSupported):
            app.get_language_url('de')

    def test_load_extensions(self):
        app = Application.load_by_key(self.client, 1768, locale='ru,en', source='/home/index')
        self.assertTrue(len(app.extensions) > 0)
        self.assertTrue(len(app.languages_by_locale) > 0)
        self.assertIsInstance(app.languages_by_locale['ru'], Language)
        self.assertIsInstance(app.sources['/home/index'], SourceTranslations)

    def test_source(self):
        app = Application.load_by_key(self.client, 1768, locale='ru,en', source='/home/index')
        source_dict = app.source('/home/index', locale='ru')
        self.assertIsInstance(source_dict, SourceDictionary, 'source dict ru')
        with self.assertRaises(LanguageNotSupported):
            h = app.sources['/home/index'].add_locale('de')

    def test_asset_url(self):
        app = Application.load_by_key(self.client, 1768, locale='ru,en', source='/home/index')
        prefix = app.tools['assets']
        self.assertEqual(prefix + '/', app.asset_url('/'))
        self.assertEqual(prefix + '/a/b/c', app.asset_url('/a/b/c'))

    def test_load(self):
        app = Application.load_by_key(self.client, 2).id
        self.assertEquals(2, Application.load_by_key(self.client, 2).id, 'Load by id')
        self.assertEquals(1, Application.load_default(self.client).id, 'Load default')


if __name__ == '__main__':
    unittest.main()

