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

from copy import copy
from .rules.contexts import Contexts
from .rules.case import Case, LazyCases
from .utils import pj, read_json
from .config import CONFIG


__author__ = 'a@toukmanov.ru, xepa4ep'

class Language(object):
    """ Language object """

    flag_url = None
    english_name = None

    def __init__(self, application, id, locale, native_name, right_to_left, contexts, cases, **kwargs):
        """ .ctor
            Args:
                application (Application): current application
                id (int): language id in API
                locale (string): language cover
                native_name (string): languge title
                right_to_left (boolean): rtl flag
                contexts (.rules.contexts.Contexts): contexts
                cases (dict): cases
        """
        self.application = application
        self.id = id
        self.locale = locale
        self.native_name = native_name
        self.right_to_left = right_to_left
        self.contexts = contexts
        self.cases = cases
        for k in kwargs:
            setattr(self, k, kwargs[k])

    @classmethod
    def cache_key(cls, locale):
        return pj(locale, 'language')

    @classmethod
    def from_dict(cls, application, data, safe=True, lazy=True):
        """ Build language instance from API response """
        data = copy(data)  # shallow copy
        if lazy:
            # Use lazy cases (do not compile all)
            cases = LazyCases(data.pop('cases', {}))
        else:
            # Compile all cases:
            cases, case_errors = Case.from_data(data.pop('cases'), safe = True)
            if len(case_errors) and not safe:
                raise Exception('Language contains invalid cases', case_errors)
        return cls(application,
                   data.pop('id', None),
                   data.pop('locale', None),
                   data.pop('native_name', None),
                   data.pop('right_to_left', None),
                   Contexts.from_dict(data.pop('contexts', {})),
                   cases,
                   **data)

    @classmethod
    def load_by_locale(cls, application, locale):
        """ Load language by locale
            Args:
                application (Application): app instance
                locale (string): locale code (ru|en)
            Throws:
                application.LanguageIsNotSupported: language is not supported by APP
                api.client.ClientError: API error
            Returns:
                Language
        """
        # check is language supported by APP:
        url = application.get_language_url(locale)
        # load data by API:
        data = application.client.get(pj(url, 'definition'), params={}, opts={'cache_key': cls.cache_key(locale)})
        # create instance:
        return cls.from_dict(application, data)

    @classmethod
    def load_default(cls, application, locale):

        def _load_default(application, locale):
            locale_path = pj(CONFIG.app_dir, 'defaults/languages', '%s.json' % locale)
            return Language.from_dict(application, read_json(locale_path), lazy=False)

        try:
            return _load_default(application, locale)
        except IOError:
            return _load_default(application, CONFIG.default_locale)

    @property
    def client(self):
        """ Client property
            Returns:
                api.client.Client
        """
        return self.application.client

    def case_by_keyword(self, case_key):
        return self.cases.get(case_key, None)

    def __eq__(self, other):
        return self.id == other.id and self.locale == other.locale

