# encoding: UTF-8
from tests.mock import Client
from tml.api.pagination import allpages
import unittest

class pagination(unittest.TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_paginantion(self):
        self.client.read('translation_keys/8ad5a7fe0a12729764e31a1e3ca80059/translations', {'page':1}, 'translation_keys/8ad5a7fe0a12729764e31a1e3ca80059/translations_1.json')
        self.client.read('translation_keys/8ad5a7fe0a12729764e31a1e3ca80059/translations', {'page':2}, 'translation_keys/8ad5a7fe0a12729764e31a1e3ca80059/translations_2.json')
        full_list = allpages(self.client, 'translation_keys/8ad5a7fe0a12729764e31a1e3ca80059/translations',{})
        self.assertEquals(3, len(full_list), 'Test paging')
        self.assertEquals(1324560, full_list[0]['id'], 'Check order')
        self.assertEquals(1324559, full_list[2]['id'], 'Check order (append to end)')

    def test_no_pagination(self):
        self.client.read('translation_keys/8ad5a7fe0a12729764e31a1e3ca80059/translations', {'page':1}, 'translation_keys/8ad5a7fe0a12729764e31a1e3ca80059/translations.json')
        full_list = allpages(self.client, 'translation_keys/8ad5a7fe0a12729764e31a1e3ca80059/translations',{})
        self.assertEquals(3, len(full_list), 'Test paging')


if __name__ == '__main__':
    unittest.main()

