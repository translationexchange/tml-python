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

__author__ = 'a@toukmanov.ru'

from .exceptions import Error

class Application(object):
    """ TML application """
    client = None # API client
    id = None # application id
    languages = None # supported language
    default_locale = None
    features = {} # key - feature code, value - boolean supported)
    key = None # client key
    name = None # human readable name
    shortcuts = {}
    tools = {} # tools URLS 

    def __init__(self, client, id, languages, default_locale, **kwargs):
        """ .ctor
            Args:
                client (api.client.Client): API client
                id (int): application id
                languages (list): list of languages
        """
        self.client = client
        self.id = id
        self.languages = languages
        self.default_locale = default_locale
        for key in kwargs:
            setattr(self, key, kwargs[key])


    @classmethod
    def from_dict(cls, client, data):
        """ Build from api response
            Args:
                client (api.client.Client): API client
                data (dict): API response
            Returns:
                Application
        """
        return Application(client, **data)


    @classmethod
    def load_default(cls, client):
        """ Load default application
            Args:
                client (api.client.Client): API client
            Returns:
                Application
        """
        return cls.from_dict(client,
                             client.get('applications/current',
                                        {'definition': 1}))

    @property
    def supported_locales(self):
        """ List of locales supported by app
            Returns:
                list
        """
        return [lang['locale'] for lang in self.languages]

    @classmethod
    def load_by_id(cls, client, id):
        """ Load application by id
            Args:
                client (api.client.Client): API client
                id (int): application
            Returns:
                Application
        """
        return cls.from_dict(client,
                             client.get('applications/%d' % id,
                                        {'definition': 1}))

    def get_language_url(self, locale):
        """ Language URL for locale
            Args:
                locale (string): locale code
            Throws:
                LanguageNotSupported
            Returns:
                string: url
        """
        for language in self.languages:
            if language['locale'] == locale:
                return 'languages/%s' % locale
        raise LanguageNotSupported(locale, self)


class LanguageNotSupported(Error):
    """ Raised if somebody try to load not supported language """
    def __init__(self, locale, application):
        """ .ctor
            Args:
                locale (string): given locale code
                application (Application): application instance
        """
        super(LanguageNotSupported, self).__init__()
        self.locale = locale
        self.application = application

    MESSAGE = 'Locale %s is not suppored by application %d'

    def __str__(self):
        return self.MESSAGE % (self.locale, self.application.id)

