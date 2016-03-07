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
from .application import Application
from .config import CONFIG
from .translation import Key
from .render import RenderEngine
from .exceptions import Error
from .dictionary import TranslationIsNotExists
from .dictionary.snapshot import SnapshotDictionary
from .language import Language
from .dictionary import NoneDict
from .dictionary.translations import Dictionary
from .dictionary.source import SourceDictionary
from .session_vars import set_current_translator, set_current_context
from .cache import CachedClient
from .utils import cached_property


__author__ = 'xepa4ep, a@toukmanov.ru'


class ContextNotConfigured(Error):
    """ Thrown if use not configured context """
    pass


class AbstractContext(RenderEngine):
    """ Wrapper for dictionary """
    language = None
    dict = None
    # _block_option_queue = []
    def __init__(self, language):
        """ .ctor
            Args:
                language (language.Language): selected language
                dictionary (dictionary.AbstractDictionary): dict object for translation
        """
        self._language = language
        self._block_option_queue = []
        super(AbstractContext, self).__init__()
        self.dict = self.build_dict(self.language)

    def push_options(self, opts):
        self._block_option_queue.append(opts)

    def pop_options(self):
        opts = self._block_option_queue.pop(-1)
        return opts

    @property
    def block_options(self):
        return self._block_option_queue and self._block_option_queue[-1] or {}

    def block_option(self, key, lookup=True, default=None):
        if lookup:
            for options in reversed(self._block_option_queue):
                if key in options:
                    return options.get(key, default)
        return self.block_options.get(key, default)

    def build_key(self, label, description, language=None):
        """ Build key """
        language = language or self.language
        return Key(label = label,
                   description = description,
                   language = language)

    def _fetch_translation(self, dict, label, description):
        key = self.build_key(label, description)
        if self.application.ignored_key(key):
            raise TranslationIsNotExists(key, self.dict)
        if dict:
            return dict.fetch(self.build_key(label, description))
        raise ContextNotConfigured(self)

    def fetch(self, label, description):
        """ Fetch Translation
            Args:
                label (string): label
                description (string): description
            Returns:
                Translation
        """
        return self._fetch_translation(self.dict, label, description)

    _default_language = None

    @property
    def default_language(self):
        """ Default language getter
            Returns:
                language.Language
        """
        if not self._default_language:
            self._default_language = self.application.language(self.default_locale)
        return self._default_language

    @property
    def language(self):
        target_locale = self.block_option('target_locale', None)
        if target_locale:
            return self.application.language(target_locale)
        else:
            return self._language

    @property
    def default_locale(self):
        """ Default locale getter
            Returns:
                string: locale name (ru, en)
        """
        return self.language.application.default_locale

    def fallback(self, label, description):
        """ Fallback translation: returns label
            Args:
                label (string)
                description (string)
            Returns:
                Translation
        """
        return self.dict.fallback(self.build_key(label, description or '', language=self.default_language))

    def tr(self, label, data = {}, description = '', options = {}):
        """ Tranlate data
            Args:
                label (string): tranlation label
                data (dict): user data
                description (string): tranlation description
                options (dict): options
                language (Language):
            Returns:
                unicode
        """
        try:
            # Get transaltion:
            translation = self.fetch(label, description)
        except TranslationIsNotExists:
            # Translation does not exists: use fallback
            translation = self.fallback(label, description)
        # Render result:
        return self.render(translation, data, options)

    def deactivate(self):
        pass

    def __del__(self):
        self.deactivate()


class LanguageContext(AbstractContext):
    """ Context with selected language """

    client = None
    key = None
    translator = None
    locale = None
    source = None

    def __init__(self, client, key=None, translator=None, locale=None, source=None, **kwargs):
        """ .ctor
            Args:
                client (Client): custom API client
                locale (string): selected locale
                source (string): which source to load in a single fetch (e.g. /home/index)
                key (int): API application key (use default if None)

        """
        CachedClient.instance().reset_version()
        self.set_translator(translator)
        if key:
            application = Application.load_by_key(
                client, key, locale=locale, source=source)
        else:
            application = Application.load_default(
                client, locale=locale, source=source)
        language = application.language(locale)
        super(LanguageContext, self).__init__(language=language)
        set_current_context(self)

    def build_dict(self, language, **kwargs):
        """ Dictionary factory (uses API directly for each fetch request) """
        return Dictionary()

    _fallback_dict = None

    @property
    def fallback_dict(self):
        """ Dictionary used if tranlation is not found in primary dictionary
            Returns:
                dictionary.AbstractDictionary
        """
        if not self._fallback_dict:
            if self.default_locale == self.locale:
                # Use default language:
                return NoneDict()
            self._fallback_dict = self.build_dict(self.default_language)
        return self._fallback_dict


    @property
    def locale(self):
        """ Selected locale getter
            Returns:
                string: locale name
        """
        return self.language.locale

    @property
    def application(self):
        """ Application getter
            Returns:
                application.Application
        """
        return self.language.application

    @property
    def client(self):
        return self.application.client

    def set_translator(self, translator):
        if not translator:
            return
        self.translator = translator
        set_current_translator(translator)

    def fallback(self, label, description):
        """ Fallback translation: try to use default language
            Args:
                label (string): tranlated label
                description (string): desctioption
            Returns:
                translation.Translation
        """
        try:
            key = Key(label = label, description = description, language = self.default_language)
            return self.fallback_dict.fetch(key)
        except TranslationIsNotExists:
            return super(LanguageContext, self).fallback(label, description)

    def is_inline_mode(self):
        return self.translator and self.translator.is_inline()

class SourceContext(LanguageContext):
    """ Context with source """
    def __init__(self, source, **kwargs):
        """ .ctor
            Args:
                source (string): source name
        """
        self.source = source   # ref name to main source
        self._used_sources = set([source])
        super(SourceContext, self).__init__(source=source, **kwargs)

    @property
    def source_name(self):   # current source: virtual or main
        return self.block_option('source', default=self.source)

    @property
    def source_path(self):
        source_builder = []
        for opts in self._block_option_queue:
            if not 'source' in opts or not opts.get('source', None):
                continue
            source_builder.append(opts['source'])
        source_builder.insert(0, self.source)
        return CONFIG['source_separator'].join(source_builder)

    def fetch(self, label, description):
        """ Fetch Translation
            Args:
                label (string): label
                description (string): description
            Returns:
                Translation
        """
        if self.source_name == self.source:
            return super(SourceContext, self).fetch(label, description)
        return self.fetch_from_virtual(label, description)

    def fetch_from_virtual(self, label, description):
        self._used_sources.add(self.source_name)
        dict = self.build_dict(self.language)
        return self._fetch_translation(dict, label, description)

    def build_dict(self, language):
        """ Fetches or builds source dictionary for language """
        source = language.application.source(self.source_name, language.locale, source_path=self.source_path)
        return source

    def deactivate(self):
        for source in self._used_sources:
            self.application.source(source, self.locale).flush()
        self._used_sources = set([])


class SnapshotContext(LanguageContext):
    """ Snapshot usage """
    def __init__(self, source, **kwargs):
        """ .ctor
            Args:
                source (string): source name
        """
        self.source = source
        super(SnapshotContext, self).__init__(source=source, **kwargs)


    def build_dict(self, language, **kwargs):
        """ Build snapshot dictionary """
        if not self.source:
            # Snapshot does not works out of source:
            return NoneDict()
        return SnapshotDictionary(self.source, language, **kwargs)


