# encoding: UTF-8
from .exceptions import Error
from .application import Application
from .language import Language
from .api.client import Client
from .dictionary.language import LanguageDictionary
from .dictionary.translations import Dictionary
from .translation import Key
from .rules.contexts.gender import Gender
from .decoration import system_tags as system_decoration_tags
from .decoration.parser import parse as parse_decoration

__author__ = 'a@toukmanov.ru'


class ContextNotConfigured(Error):
    pass


class Context(object):
    """ Execution context """
    def __init__(self, **kwargs):
        self.language = None
        self.missed_keys = None
        self.dict = None
        if len(kwargs):
            self.configure(**kwargs)


    def configure(self, token, locale = None, application_id = None, preload = False, flush_missed = True, client = None, decoration_tags = None):
        """ Configure tranlation
            Args:
                token (string): API token
                locale (string): selected locale
                application_id (int): API application id (use default if None)
                preload (boolean): preload all tranlations
                flush_missed (boolean): flush missed immediatly (if false - keys flushed with flush_keys)
                client (Client): custom API client
                decoration_tags (TagsFactory): custom decoration tags
        """
        self.language = self.build_language(locale,
                                            self.build_application(application_id,
                                                                   self.build_client(token, client)))
        if flush_missed:
            # flush missed immediate
            self.missed_keys = MissedKeys(self.language.client)
        else:
            # flush missed with flush_missed
            self.missed_keys = MissedKeysLazy(self.language.client)
        if preload:
            # Preload all translations for languge:
            self.dict = LanguageDictionary(self.language)
        else:
            # Load tranlations on demand: 
            self.dict = Dictionary()
        # Init decoration tags:
        self.decoration_tags = decoration_tags or system_decoration_tags
        return self

    def build_language(self, locale, app):
        """ Build application from configuration
            Args:
                locale (string): locale (if None - use application default)
                app (Application): Application
            Returns:
                Language
        """
        if locale is None:
            locale = app.default_locale
        return Language.load_by_locale(app, locale)

    def build_application(self, app_id, client):
        """ Build application from configuration
            Args:
                app_id (int): Application id
                client (Client): API client
            Returns:
                Application
        """
        if app_id:
            return Application.load_by_id(client, app_id)
        else:
            return Application.load_default(client)

    def build_client(self, token, client):
        """ Build client from configuration
            Args:
                token (string): API token
                client (Client): custom API client
            Returns:
                Client
        """
        if client:
            return client
        return Client(token)


    def tr(self, label, data = {}, description = '', options = {}):
        """ Tranlate data
            Args:
                label (string): tranlation label
                data (dict): user data
                description (string): tranlation description
                options (dict): options 
                language (Language):
        """
        if self.dict is None:
            raise ContextNotConfigured('Translation is not configured')
        # Translate data:
        t = self.dict.translate(Key(label = label, description = description, language = self.language))
        # Apply tokens:
        ret = t.execute(data, options)
        # Apply decoration:
        return parse_decoration(ret).render(options)

    def submit_missed(self):
        """ Submit missed key to server after app is executed """
        if self.missed_keys is None:
            raise ContextNotConfigured('Translation is not configured')
        self.missed_keys.submit_all()

    @property
    def locale(self):
        return self.language.locale

    @property
    def application(self):
        return self.language.application


context = Context()


def configure(**kwargs):
    return context.configure(**kwargs)


def tr(label, data = {}, description = '', options = {}):
    """ Tranlate data
        Args:
            label (string): tranlation label
            data (dict): user data
            description (string): tranlation description
            language (Language):
            options (dict): options 
    """
    return context.tr(label, data, description, options)


def submit_missed():
    return context.submit_missed()


