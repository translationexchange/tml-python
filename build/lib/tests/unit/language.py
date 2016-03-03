from __future__ import absolute_import
# encoding: UTF-8
import unittest
from tml.application import Application, LanguageNotSupported
from tml.language import Language
from os.path import dirname
import json
from tml.rules.contexts import Contexts
from tests.mock import Client

LANGUAGES = [
    {'id': 233, 'locale':'ru', 'native_name': 'Русский', 'right_to_left': False},
    {'id': 2, 'locale':'en', 'native_name': 'English', 'right_to_left': False}]


class LanguageTest(unittest.TestCase):
    """ Language tests"""
    def setUp(self):
        self.client = Client()
        self.client.read('languages/ru/definition', None)
        self.app = Application(self.client, 100, [{'id': 233, 'locale':'ru', 'native_name': 'Русский', 'right_to_left': False}], 'en')

    def test_load(self):
        """ Load language """
        lang = Language.load_by_locale(self.app, 'ru')
        self.assertEquals(233, lang.id, 'id')
        self.assertEquals('ru', lang.locale, 'locale')
        self.assertFalse(lang.right_to_left, 'right_to_left')
        self.assertTrue(isinstance(lang.contexts, Contexts), 'Contexts fetched')
        self.assertEquals(self.app, lang.application, 'test application')
        with self.assertRaises(LanguageNotSupported):
            Language.load_by_locale(self.app, 'de')


if __name__ == '__main__':
    unittest.main()

