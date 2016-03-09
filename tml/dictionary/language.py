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

from ..utils import pj
from . import Hashtable
from tml.api.pagination import allpages

class LanguageDictionary(Hashtable):
    """ Load tranlations for language """
    def __init__(self, lang, fallback=None, translations=None):
        """ .ctor
            Args:
                lang (Language): language
        """
        self.language = lang
        translations = translations or self.fetch_translations()
        super(LanguageDictionary, self).__init__(translations=translations, fallback=fallback)

    @property
    def cache_key(self):
        return pj(self.language.locale, 'translations')

    def load_translations(self, translations=None):
        if translations:
            self.translations = translations
        elif self.translations:
            pass
        else:
            self.translations = self.fetch_translations()

    def fetch_translations(self):
        uri, params, opts = self.api_query
        return allpages(self.language.client, uri, params=params, opts=opts)

    @property
    def api_query(self):
        """ Params to API call
            Returns:
                tuple: url, params
        """
        return ('projects/%d/translations' % self.language.application.id,
                {'locale': self.language.locale},
                {'cache_key': self.cache_key})
