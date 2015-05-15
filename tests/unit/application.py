from __future__ import absolute_import
# encoding: UTF-8
import unittest
from tml.application import Application, LanguageNotSupported
from tests.mock import Client

LANGUAGES = [{'locale':'ru'},{'locale':'en'}]

class ApplicationTest(unittest.TestCase):

    def setUp(self):
        self.client = Client.read_all()

    def test_instance(self):
        app = Application.from_dict(self.client, {'id':100, 'languages': LANGUAGES, 'default_locale':'en'})
        self.assertEquals(100, app.id, 'id getter')
        self.assertEquals(LANGUAGES, app.languages, 'Check languages')
        self.assertEquals('en', app.default_locale, 'Default locale')


    def test_language(self):
        app = Application(self.client, 100, LANGUAGES, 'en')
        self.assertEquals('languages/ru', app.get_language_url('ru'), 'URL for ru')
        self.assertEquals('languages/en', app.get_language_url('en'), 'URL for en')
        with self.assertRaises(LanguageNotSupported):
            app.get_language_url('de')

    def test_load(self):
        self.assertEquals(2, Application.load_by_id(self.client, 2).id, 'Load by id')
        self.assertEquals(1, Application.load_default(self.client).id, 'Load default')


if __name__ == '__main__':
    unittest.main()

