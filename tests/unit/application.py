# encoding: UTF-8
import unittest
from tml import Application, LanguageNotSupported

class ClientMock(object):
    def __init__(self, data = {}):
        self.data = data

    def get(self, url, params):
        return self.data[url]

LANGUAGES = [{'locale':'ru'},{'locale':'en'}]

class application(unittest.TestCase):
    def test_instance(self):
        app = Application.from_dict(ClientMock(), {'id':100, 'languages': LANGUAGES})
        self.assertEquals(100, app.id, 'id getter')
        self.assertEquals(LANGUAGES, app.languages, 'Check languages')


    def test_language(self):
        app = Application(ClientMock(), 100, LANGUAGES)
        self.assertEquals('languages/ru', app.get_language_url('ru'), 'URL for ru')
        self.assertEquals('languages/en', app.get_language_url('en'), 'URL for en')
        with self.assertRaises(LanguageNotSupported):
            app.get_language_url('de')

    def test_load(self):
        c = ClientMock({'applications/10': {'id': 10, 'languages': LANGUAGES},
                        'applications/current':{'id':20, 'languages': []}})
        self.assertEquals(10, Application.load_by_id(c, 10).id, 'Load by id')
        self.assertEquals(20, Application.load_default(c).id, 'Load default')


if __name__ == '__main__':
    unittest.main()

