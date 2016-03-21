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

__author__ = 'a@toukmanov.ru, xepa4ep'

from six import iteritems
from .exceptions import Error
from .language import Language
from .source import SourceTranslations
from .config import CONFIG
from .session_vars import get_current_translator
from .logger import get_logger
from .translation.missed import MissedKeys


class Application(object):
    """ TML application """
    client = None # API client
    id = None # application id
    languages = None # supported languages
    default_locale = None
    languages_by_locale = None
    features = None # key - feature code, value - boolean supported)
    key = None # client key
    name = None # human readable name
    shortcuts = None
    tools = None # tools URLS
    extensions = None
    css = None

    cache_key = 'application'

    def __init__(self, client=None, key=None, languages=None, default_locale=None, **kwargs):
        """ .ctor
            Args:
                client (api.client.Client): API client
                id (int): application id
                languages (list): list of languages
        """
        self.client = client or self.build_default_client()
        self.key = key
        self.sources = {}
        self.languages_by_locale = {}
        self.languages = [Language.from_dict(self, lang_meta) for lang_meta in languages or []]
        self.default_locale = default_locale
        self.load_extensions(kwargs.get('extensions', {}))
        for key in kwargs:
            setattr(self, key, kwargs[key])
        translator = get_current_translator()
        if translator is not None:   # if we initialized with active translator session
            translator.set_application(self)
        self.missed_keys = MissedKeys(self.client)

    @classmethod
    def from_dict(cls, client, data):
        """ Build from api response
            Args:
                client (api.client.Client): API client
                data (dict): API response
            Returns:
                Application
        """
        return Application(client=client, **data)

    @classmethod
    def load_default(cls, client, source=None, locale=None):
        """ Load default application
            Args:
                client (api.client.Client): API client
            Returns:
                Application
        """
        return cls.load_by_key(client, key=CONFIG.application_key(), source=source, locale=locale)

    @property
    def supported_locales(self):
        """ List of locales supported by app
            Returns:
                list
        """
        return [lang.locale for lang in self.languages]

    @classmethod
    def load_by_key(cls, client, key, locale=None, source=None):
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
        default_dict = {'key': key}
        app_dict = client.get(
            'projects/%s/definition' % key,
            params={'locale': locale, 'source': source, 'ignored': True},
            opts={'cache_key': cls.cache_key})
        # import pdb
        # pdb.set_trace()
        if 'results' in app_dict:
            app_dict = app_dict['results']
        application = cls.from_dict(client, app_dict or default_dict)
        if not app_dict:  # if empty application
            application.add_language(Language.load_default(application, locale))
        return application

    def load_extensions(self, extensions):
        """Load application extensions if any"""
        if not extensions:
            return
        source_locale = self.default_locale
        for locale, data in iteritems(extensions.get('languages', {})):
            if self.default_locale != locale:
                source_locale = locale
            self.languages_by_locale[locale] = Language.from_dict(self, data)
        for source, data in iteritems(extensions.get('sources', {})):
            self.sources.setdefault(
                source,
                SourceTranslations(source, self).add_locale(source_locale, **data))

    @property
    def token(self):
        return self.client.token

    def language(self, locale=None, fallback_to_dummy=True):

        def lang_(app, locale, target_locale=None):
            target_locale = locale if target_locale is None else target_locale
            try:
                return app.languages_by_locale.setdefault(locale, Language.load_by_locale(app, target_locale))
            except LanguageNotSupported:
                pass

        def base_lang_(app, locale):
            if not '-' in locale:
                return
            base_locale = locale.split('-')[0]
            return lang_(app, locale, target_locale=base_locale)
        locale = self._normalize_locale(locale)
        if self.languages_by_locale.get(locale, None):
            return self.languages_by_locale[locale]
        language = lang_(self, locale) or base_lang_(self, locale)
        if language:
            return language

        if fallback_to_dummy:
            return self.languages_by_locale.setdefault(locale, Language.load_default(self, locale))
        else:
            raise LanguageNotSupported(locale, self)

    def _normalize_locale(self, locale):
        if locale is None:
            locale = self.default_locale or CONFIG.default_locale
        return locale.strip().replace('_', '-')  # normalize locale

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

    def source(self, source, locale, **init_kwargs):
        """ .ctar
            Params:
                source (string) - source name
                locale (string) - locale e.g. ru
            Returns:
                dictionary.SourceDictionary or None"""
        source_translations = self.sources.get(source, None)
        if not source_translations:
            source_translations = self.sources[source] = SourceTranslations(source, self)
        return source_translations.add_locale(locale, **init_kwargs).hashtable_by_locale(locale)

    def verify_source_path(self, source_key, source_path):
        # 1. cache enabled and TM turned off
        if CONFIG.cache_enabled() and not self.is_inline_mode():
            return
        # 2. app does not use sources here
        if not self.extensions or not self.extensions.get('sources', None):
            return
        # 3. if this source is already registered under the main source
        if source_key in self.extensions['sources']:
            return
        # 4. otherwise register nested source
        self.missed_keys.register(source_path)

    def is_inline_mode(self):
        translator = get_current_translator()
        return translator and translator.is_inline()

    def ignored_key(self, key):
        _key = key.key

        for source_translations in self.sources.values():
            if source_translations.is_ignored(_key):
                self.logger.debug('Ignored Key[%s]: %s', _key, key.label)
                return True
        return False

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
        if not self.features:
            return True
        return self.features.get(key, False)

    @property
    def logger(self):
        return get_logger()

    def register_missing_key(self, key, source_path):
        self.missed_keys.append(key, source_path)
        if CONFIG.is_interactive_mode():
            self.flush()

    def flush(self):
        self.missed_keys.submit_all()


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

    MESSAGE = 'Locale %s is not suppored by application %s'

    def __str__(self):
        return self.MESSAGE % (self.locale, self.application.key)

