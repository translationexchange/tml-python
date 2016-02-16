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
from .language import Language
from .source import SourceTranslations


class Application(object):
    """ TML application """
    client = None # API client
    id = None # application id
    languages = None # supported languages
    languages_by_locale = {}  #
    sources = {}   # contained under 'extensions' key
    default_locale = None

    features = {} # key - feature code, value - boolean supported)
    key = None # client key
    name = None # human readable name
    shortcuts = {}
    tools = {} # tools URLS
    extensions = {}

    def __init__(self, client, id, languages, default_locale, **kwargs):
        """ .ctor
            Args:
                client (api.client.Client): API client
                id (int): application id
                languages (list): list of languages
        """
        self.client = client
        self.id = id
        self.languages = [Language.from_dict(self, lang_meta) for lang_meta in languages]
        self.default_locale = default_locale
        self.load_extensions(kwargs.get('extensions', {}))
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
    def load_default(cls, client, source=None, locale=None):
        """ Load default application
            Args:
                client (api.client.Client): API client
            Returns:
                Application
        """
        return cls.from_dict(client, client.get('projects/current/definition', {'source': source, 'locale': locale}))


    @property
    def supported_locales(self):
        """ List of locales supported by app
            Returns:
                list
        """
        return [lang.locale for lang in self.languages]

    @classmethod
    def load_by_id(cls, client, id, locale=None, source=None):
        """ Load application by id
            Args:
                client (api.client.Client): API client
                id (int): application
            Kwargs:
                locale: locale string serapated by `,` (e.g. ru-RU,ru,en-US,en),
                source: source string separated by ',' (e.g. /home/index)
            Returns:
                Application
        """
        return cls.from_dict(client, client.get('projects/%s/definition' % id,
                                        {'locale': locale, 'source': source, 'ignored': True}))

    def load_extensions(self, extensions):
        """Load application extensions if any"""
        if not extensions:
            return
        source_locale = self.default_locale
        for locale, data in extensions.get('languages', {}).iteritems():
            if self.default_locale != locale:
                source_locale = locale
            self.languages_by_locale[locale] = Language.from_dict(self, data)
        for source, data in extensions.get('sources', {}).iteritems():
            self.sources.setdefault(
                source,
                SourceTranslations(source, self).add_locale(source_locale, **data))

    def language(self, locale=None):
        if locale is None:
            locale = self.default_locale
        locale = locale.strip()
        return self.languages_by_locale.setdefault(locale, Language.load_by_locale(self, locale))

    def default_language(self):
        return self.language(locale=self.default_locale)

    def add_language(self, new_language):
        if new_language.locale in self.languages_by_locale:
            return self.languages_by_locale[new_language.locale]
        self.languages_by_locale[new_language.locale] = new_language
        self.languages.append(new_language)
        return new_language

    def locales(self):
        return list(lang.locale for lang in self.languages)

    def asset_url(self, path):
        if not path.startswith('/'):
            path = '/' + path
        return "%s%s" % (self.tools['assets'], path)

    def source(self, source, locale):
        """ .ctar
            Params:
                source (string) - source name
                locale (string) - locale e.g. ru
            Returns:
                dictionary.SourceDictionary or None"""
        source_translations = self.sources.get(source, None)
        if not source_translations:
            source_translations = self.sources[source] = SourceTranslations(source, self) #.add_locale(locale)
        return source_translations.add_locale(locale).hashtable_by_locale(locale)

    def get_language_url(self, locale):
        """ Language URL for locale
            Args:
                locale (string): locale code
            Throws:
                LanguageNotSupported
            Returns:
                string: url
        """

        def from_list(locale):
            filtered = (lang for lang in self.languages if lang.locale == locale)
            return next(filtered, None)

        def from_map(locale):
            return self.languages_by_locale.get(locale, None)

        language = from_list(locale) or from_map(locale)
        if not language:
            raise LanguageNotSupported(locale, self)
        return 'languages/%s' % locale
    
    def feature_enabled(self, key):
        return self.features.get(key, False)


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

