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
from hashlib import md5
from ..utils import pj
from ..translation.missed import MissedKeys
from ..api import APIError
from ..cache import CachedClient
from ..session_vars import get_current_context
from ..config import CONFIG
from tml.dictionary import TranslationIsNotExists


class SourceDictionary(Hashtable):
    """ Dictionary of keys grouped by source """
    def __init__(self, source, language, source_path=None, fallback=None, translations=None):
        """ .ctor
            Args:
                source (string): source name
                lang (Language): language
                missed_keys (list): list of missed keys
        """
        self.source = source
        self.source_path = source_path or source
        self.language = language
        if translations is None:
            translations = self.fetch_translations()
        super(SourceDictionary, self).__init__(translations=translations, fallback=fallback)

    @property
    def application(self):
        return self.language.application

    @property
    def context(self):
        return get_current_context()

    @property
    def key(self):
        return self.compute_key()

    def cache_key(self):
        return pj(self.language.locale, 'sources', *self.source.split('/'))

    def compute_key(self):
        return md5(self.source.encode('utf-8')).hexdigest()

    def load_translations(self, translations=None):
        """Load translations.
        Logic:
            1. if `translations` passed, then reset old with new one
            2. if self.translations is set, then no op
            3. in all other cases, fetch translations from api"""
        if translations:
            self.translations = translations
        elif self.translations is not None:
            pass
        else:
            self.translations = self.fetch_translations()
        return self

    def fetch_translations(self):
        try:
            uri, params, opts = self.api_query
            result = self.language.client.get(uri, params=params, opts=opts)
        except APIError:
            return {}
        else:
            return result.get('results', result)

    @property
    def api_query(self):
        """ Params to API call
            Returns:
                tuple: url, params
        """
        # import pdb
        # pdb.set_trace()
        return ('sources/%s/translations' % self.key,
                {'locale': self.language.locale, 'all': True, 'ignored': True},
                {'cache_key': self.cache_key()})

    def fetch(self, key):
        try:
            ret = super(SourceDictionary, self).fetch(key)
        except TranslationIsNotExists as translation_not_exists:
            if key.label:
                self.application.register_missing_key(key, self.source_path)
                translation_not_exists.make_pending()
            raise translation_not_exists
        if len(ret) == 0:
            """ Empty translation """
            raise TranslationIsNotExists(key, self)
        return ret

    def verify_path(self):
        """Source is registered under main source, if not registered yet."""
        self.application.verify_source_path(self.source, self.source_path)
