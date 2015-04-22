# encoding: UTF-8
from tml.api.snapshot import open_snapshot
import unittest
from tml.dictionary.snapshot import SnapshotDictionary
from tml import Key, Language, Application
from tests.mock import FIXTURES_PATH

class SnapshotTest(unittest.TestCase):
    """ Test loading tranlations over API """
    def setUp(self):
        self.client = open_snapshot('%s/snapshot.tar.gz' % FIXTURES_PATH)
        self.app = Application.load_default(self.client)
        self.lang = Language.load_by_locale(self.app, 'ru')

    def test_translate(self):
        dict = SnapshotDictionary(language = self.lang, source = 'index')
        t = dict.translate(Key(label = 'Test',
                              language = self.lang))
        self.assertEquals(u'Тест', t.execute({}, {}), 'Test translate')
        t = dict.translate(Key(label = 'Untranslated',
                              language = self.lang))
        self.assertEquals(u'Untranslated', t.execute({}, {}), 'Test fallback')


if __name__ == '__main__':
    unittest.main()

