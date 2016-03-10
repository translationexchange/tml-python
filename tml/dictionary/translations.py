# encoding: UTF-8
"""
# Basic translation dict - call API for each translation
#
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

from . import AbstractDictionary
from ..utils import pj
from ..api.pagination import allpages
from ..translation import Translation
from ..api.client import ClientError
from . import TranslationIsNotExists


class Dictionary(AbstractDictionary):
    """ Dictionary fetch translation for each key via API """

    def __init__(self, *a, **kw):
        super(Dictionary, self).__init__(*a, **kw)
        self.translations = {}

    def cache_key(self, locale, key):
        return pj(locale, 'keys', key)

    def fetch(self, key):
        """ Translate key
            Args:
                key (Key): tranlated key
            Returns:
                Translation
        """
        if self.translations.get(key.key, None):
            return Translation.from_data(key, self.translations[key.key])
        try:
            self.translations[key.key] = data = key.client.get(
                'translation_keys/%s/translations' % key.key,
                params={'locale': key.language.locale, 'all': True},
                opts={'cache_key': self.cache_key(key.language.locale, key.key)}).get('results', [])

            return Translation.from_data(key, data)
        except ClientError as e:
            raise TranslationIsNotExists(key, self)

