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
from ..translation.missed import MissedKeys
from tml.dictionary import TranslationIsNotExists


class SourceMissed(MissedKeys):
    """ Set of missed keys in source """
    def __init__(self, client, source):
        """ .ctor
            Args:
                client (tml.api.AbstractClient): API client
                source (string): source name
        """
        super(SourceMissed, self).__init__(client)
        self.source = source

    def as_dict(self):
        """ Dict repr for API call """
        ret = super(SourceMissed, self).as_dict()
        ret.update({'source': self.source})
        return ret


class SourceDictionary(Hashtable):
    """ Dictionary of keys grouped by source """
    def __init__(self, source, language, fallback = None):
        """ .ctor 
            Args:
                source (string): source name
                lang (Language): language
                missed_keys (list): list of missed keys
        """
        self.source = source
        self.language = language
        self.missed_keys = SourceMissed(self.language.client, source)
        data = self.language.client.get(*self.api_query)
        super(SourceDictionary, self).__init__(data['results'], fallback)

    @property
    def api_query(self):
        """ Params to API call 
            Returns:
                tuple: url, params
        """
        uri = md5(self.source.encode('utf-8')).hexdigest()
        return ('sources/%s/translations' % uri,
                {'locale': self.language.locale})

    def fetch(self, key):
        try:
            ret = super(SourceDictionary, self).fetch(key)
        except TranslationIsNotExists as translation_not_exists:
            self.missed_keys.append(key)
            raise translation_not_exists
        if len(ret) == 0:
            """ Empty translation """
            raise TranslationIsNotExists(key, self)
        return ret

    def __del__(self):
        self.flush()

    def flush(self):
        """ Submit all missed keys on delete """
        if self.missed_keys.submit_all():
            self.language.client.reload(*self.api_query)

