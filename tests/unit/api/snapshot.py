# encoding: UTF-8
"""
# Copyright (c) 2015, Translation Exchange, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from __future__ import absolute_import
from tml.api.snapshot import SnapshotFile, SnapshotDir, MethodIsNotSupported,\
    open_snapshot, rewrite_path
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
        self.assertEquals('application', rewrite_path('applications/current'), 'Rewrite application path')
        self.assertEquals('de/language', rewrite_path('languages/de'), 'Rewrite language path')
        self.assertEquals('ru/sources/test', rewrite_path('ru/sources/test'), 'Do not rewrite sources path')

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
                          client.get('ru/sources/yyyy', {}),
                          'Load source')
        with self.assertRaises(APIError) as c:
            client.get('de/sources/notexists')

        with self.assertRaises(MethodIsNotSupported) as c:
            client.post('some/url', {})

