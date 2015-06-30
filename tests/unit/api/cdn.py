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

import unittest
import requests_mock
from tml.api.cdn import Client as CDNClient, CDN_VERSION_URL
from tml.api.client import Client as APIClient
from tests.mock import FIXTURES_PATH
from tml import Application, Language, SnapshotContext
from tml.strings import to_string
from json import loads

VERSION = 20150612185759
TOKEN = 'token'

class CdnTest(unittest.TestCase):
    @requests_mock.mock()
    def test_version(self, m):
        """ Test fetch current version """
        m.get('%s/%s/%s' % (APIClient.API_HOST, APIClient.API_PATH, CDN_VERSION_URL), json = VERSION)
        self.assertEquals(VERSION, CDNClient.current_version(APIClient(TOKEN)))

    @requests_mock.mock()
    def test_rewrite(self, m):
        """ Test rewrite """
        with open(FIXTURES_PATH+'/applications/current.json') as fp:
            m.get(CDNClient.URL % (TOKEN, VERSION, 'application'), json = loads(fp.read()))
        with open(FIXTURES_PATH+'/languages/ru.json') as fp:
            m.get(CDNClient.URL % (TOKEN, VERSION, 'ru/language'), json = loads(fp.read()))
        with open(FIXTURES_PATH+'/snapshot/ru/sources/alpha.json') as fp:
            m.get(CDNClient.URL % (TOKEN, VERSION, 'ru/sources/alpha'), json = loads(fp.read()))
        client = CDNClient(TOKEN, VERSION)
        application = Application.load_default(client)
        self.assertEquals(1, application.id, 'Check load application')
        language = Language.load_by_locale(application, 'ru')
        self.assertEqual('ru', language.locale,'Check load language')
        c = SnapshotContext('alpha', client = client, locale = 'ru')
        print c.tr('Hello {name}', {'name': str('Вася')})
        self.assertEquals(to_string('Привет Вася'), c.tr('Hello {name}', {'name': to_string('Вася')}),'Check source translation')