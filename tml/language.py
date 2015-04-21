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

from .rules.contexts import Contexts
from .rules.case import Case


__author__ = 'a@toukmanov.ru'

class Language(object):
    """ Language object """
    def __init__(self, application, language_id, locale, native_name, right_to_left, contexts, cases):
        """ .ctor
            Args:
                application (Application): current application
                language_id (int): language id in API
                locale (string): language cover
                native_name (string): languge title
                right_to_left (boolean): rtl flag
                contexts (.rules.contexts.Contexts): contexts
                cases (dict): cases
        """
        self.application = application
        self.id = language_id
        self.locale = locale
        self.native_name = native_name
        self.right_to_left = right_to_left
        self.contexts = contexts
        self.cases = cases

    @classmethod
    def from_dict(cls, application, data, safe = True):
        """ Build language instance from API response """
        cases, case_errors = Case.from_data(data['cases'], safe = True)
        if len(case_errors) and not safe:
            raise Exception('Language contains invalid cases', case_errors)
        return cls(application,
                   data['id'],
                   data['locale'],
                   data['native_name'],
                   data['right_to_left'],
                   Contexts.from_dict(data['contexts']),
                   cases)

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
        data = application.client.get(url, {'definition': 1})
        # create instance:
        return cls.from_dict(application, data)

    @property
    def client(self):
        """ Client property
            Returns:
                api.client.Client
        """
        return self.application.client

