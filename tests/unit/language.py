# encoding: UTF-8
import unittest
from tml import Application, LanguageNotSupported
from tml.language import Language
from os.path import dirname
import json
from tml.rules.contexts import Contexts

class ClientMock(object):
    def __init__(self, data = {}):
        self.data = data

    def get(self, url, params):
        return self.data[url]

LANGUAGES = [{'locale':'ru'},{'locale':'en'}]

class language(unittest.TestCase):
    """ Language tests"""
    def setUp(self):
        path = '%s/fixtures/ru.json' % dirname(dirname(__file__))
        ru = json.loads(open(path).read())
        self.client = ClientMock({'languages/ru': ru})
        self.app = Application(self.client, 100, [{'locale':'ru'}])

    def test_load(self):
        """ Load language """
        lang = Language.load_by_locale(self.app, 'ru')
        self.assertEquals(233, lang.id, 'id')
        self.assertEquals('ru', lang.locale, 'locale')
        self.assertFalse(lang.right_to_left, 'right_to_left')
        self.assertTrue(isinstance(lang.contexts, Contexts), 'Contexts fetched')
        with self.assertRaises(LanguageNotSupported):
            Language.load_by_locale(self.app, 'de')


if __name__ == '__main__':
    unittest.main()

