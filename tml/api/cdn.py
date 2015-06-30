# encoding: UTF-8
"""
# Copyright (c) 2015, Translation Exchange, Inc.
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
from tml.strings import to_string
from .client import Client as BaseClient, HttpError
from .snapshot import wrap_call
import requests

__author__ = 'a@toukmanov.ru'

CDN_VERSION_URL = 'applications/current/version'

class Client(BaseClient):
    """ CDN client """
    def __init__(self, token, version):
        super(Client, self).__init__(token)
        self.version = version

    @classmethod
    def current_version(self, client):
        """
        Build CDN client for current version
        :param client: API client (to fetch current version)
        :type client: AbstractClient
        :return: new client
        :rtype: Client
        """
        return client.get(CDN_VERSION_URL)

    URL = 'http://cdn.translationexchange.com/%s/%d/%s.json'

    @wrap_call
    def call(self, url):
        """
        Call API method (only GET allowed, URL overwritten as snapshot)
        :param url: URL
        :return: dict API response
        """
        url = self.URL % (self.token, self.version, url)
        try:
            resp = requests.get(url)
            if resp.status_code != 200:
                raise Exception('Unexpected status %d' % resp.status_code)
            return resp.json()
        except Exception as http_error:
            raise HttpError(http_error,
                url = url,
                client = self)

