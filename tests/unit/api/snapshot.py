# encoding: UTF-8
from __future__ import absolute_import
from tml.api.snapshot import SnapshotFile, SnapshotDir, MethodIsNotSupported,\
    open_snapshot
from tests.mock import FIXTURES_PATH
import unittest
from tml.application import Application
from tml.language import Language
from tml.api.client import APIError
from tml import Error
from tml.strings import to_string


class SnapshotTest(unittest.TestCase):
    """ Test for snapshot API client """
    def test_rewrite(self):
        c = SnapshotFile('%s/snapshot.tar.gz' % FIXTURES_PATH)
        self.assertEquals('application', c.rewrite_path('projects/current/definition'), 'Rewrite application path')
        self.assertEquals('de/language', c.rewrite_path('languages/de/definition'), 'Rewrite language path')
        self.assertEquals('ru/sources/test', c.rewrite_path('ru/sources/test'), 'Do not rewrite sources path')

    def test_load_from_tar(self):
        client = SnapshotFile('%s/snapshot.tar.gz' % FIXTURES_PATH)
        self.check_load(client)

    def test_load_from_dir(self):
        client = SnapshotDir('%s/snapshot/' % FIXTURES_PATH)
        self.check_load(client)

    def test_detect_type(self):
        self.assertEqual(SnapshotDir, open_snapshot('%s/snapshot/' % FIXTURES_PATH).__class__, 'Open snapshot dir')
        self.assertEqual(SnapshotFile, open_snapshot('%s/snapshot.tar.gz' % FIXTURES_PATH).__class__, 'Open snapshot file')
        with self.assertRaises(Error):
            open_snapshot('%s/notexists_path' % FIXTURES_PATH)

    def check_load(self, client):
        app = Application.load_default(client)
        self.assertEquals(767, app.id, 'Load application')
        self.assertEquals('ru', Language.load_by_locale(app, 'ru').locale, 'Load language')
        self.assertEquals({"results":{"90e0ac08b178550f6513762fa892a0ca":[{"label":to_string("Привет {name}")}]}},
                          client.get('ru/sources/yyyy', params={}),
                          'Load source')
        with self.assertRaises(APIError) as c:
            client.get('de/sources/notexists')

        with self.assertRaises(MethodIsNotSupported) as c:
            client.post('some/url', params={})

