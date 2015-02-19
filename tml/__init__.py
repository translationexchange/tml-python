# -*- coding: utf-8 -*-
from api import Client
from .cache import CachedClient
from .application import Application
from .language import Language
from .expetions import Error
from .group import LanguageGroup, NullGroup
from django.template.defaulttags import load
from .utils import cached_property

class Translation(object):
    """ Translation settings """
    readonly = False
    prefetch = False
    def __init__(self, token, app_id = None, cache_backend = None, prefetch = True, readonly = False):
        """ Init tranlation
            Args:
                token (string): API token
                app_id (int): application id (if not set- load default application)
                cache_backend (Cache): cache backend for API client
                prefetch (boolean): prefetch all phrases for group
                readonly (boolean): do not notify about missed keys
        """
        client = Client(token)
        if not cache_backend is None:
            # Use cache for backend:
            client = CachedClient(client, cache_backend)
        if app_id is None:
            # Use default application:
            self.app = Application.current(client)
        else:
            # Load application from configuration:
            self.app = Application.load_by_id(app_id, client)
        self._language = None
        self._group = None
        self.prefetch = prefetch

    def set_locale(self, locale):
        """ Select application language
            Args:
                locale (string): locale code
            Throws:
                LanguageDoesNotExists
        """
        self._language = Language.load(application = self.app, locale = locale)
        self._group = None
        return self

    @cached_property
    def language(self):
        """ Language getter """
        return Language.default(self.app)

    @property
    def group(self):
        if self.prefetch:
            return LanguageGroup(self.language)
        else:
            # Do not prefetch
            return NullGroup()

    def fetch_translation(self, label, description = ''):
        key = TranslationKey(label, description, self.language)
        try:
            # Load translation for current language and apply
            return self.group.translate(key)
        except Exception as e:
            key.missed()
            # Use label to build translation:
            return Translation(key, [label])

_translation = None

def configure(token, app_id = None, locale = None, cache_backend = None, readonly = False, prefetch = False):
    """ Configure page """
    _translation = Translation(app_id, locale, cache_backend)

def set_locale(locale):
    _translation.set_locale(locale)

def tr(label, tokens = {}, description = '', oprions = {}):
    if _translation is None:
        raise Error('Translation is not configured')
    key = TranlationKey(label, description)
