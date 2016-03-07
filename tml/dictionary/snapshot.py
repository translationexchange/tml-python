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

__author__ = 'a@toukmanov.ru'

from . import Hashtable
from ..api import ClientError

class SnapshotDictionary(Hashtable):
    """ .ctor """
    def __init__(self, source, language, fallback = None, translations=None):
        self.source = source
        self.language = language
        try:
            translations = translations or self.fetch_translations()
            super(SnapshotDictionary, self).__init__(translations=translations)
        except ClientError:
            # empty dictionary:
            super(SnapshotDictionary, self).__init__({})

    def load_translations(self):
        self.translations = self.fetch_translations()

    def fetch_translations(self):
        try:
            result = self.language.client.get(*self.api_query)['results']
        except ApiError:
            return {}
        else:
            return result.get('results', result)

    @property
    def api_query(self):
        return ('%s/sources/%s' % (self.language.locale, self.source),)

