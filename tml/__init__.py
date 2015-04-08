# encoding: UTF-8
from .exceptions import Error
from .application import Application
from .language import Language
from .api.client import Client
from .dictionary import Hashtable
from .dictionary.translations import Dictionary
from .dictionary.source import SourceDictionary
from .translation import Key
from .rules.contexts.gender import Gender
from .decoration import system_tags as system_decoration_tags
from .decoration.parser import parse as parse_decoration
from .tools import Renderable
from argparse import ArgumentError
from .dictionary import AbstractDictionary


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


    def configure(self, token = None, locale = None, source = None, application_id = None, client = None, decoration_tags = None, use_fallback_dictionary = True):
        """ Configure tranlation
            Args:
                token (string): API token
                locale (string): selected locale
                application_id (int): API application id (use default if None)
                preload (boolean): preload all tranlations
                client (Client): custom API client
                decoration_tags (TagsFactory): custom decoration tags
                use_fallback_dictionary (Boolean): use fallback dictionart
        """
        self.language = self.build_language(locale,
                                            self.build_application(application_id,
                                                                   self.build_client(token, client)))
        handle = Exception if use_fallback_dictionary else None
        try:
            if isinstance(source, Abstra):
                # dictionary instance passed:
                self.dict = source
            elif source:
                self.dict = SourceDictionary(language = self.language, source = source)
            else:
                self.dict = Dictionary()
        except handle:
            self.dict = Hashtable({})
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
        ret = t.execute(self.prepare_data(data), options)
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

    # List of objects which preprocess data before translation:
    data_preprocessors = []
    env_generators = []

    def prepare_data(self, data):
        """ Prepare data for render 
            Args:
                data (dict): raw data
            Returns:
                dict: data after modification
        """
        return DataInContext(data, self)

context = Context()

class DataInContext(object):
    """ Render data on demand """
    def __init__(self, data, context):
        """ .ctor
            data (dict): user data
            context (tml.Context): translation context (current language etc.)
        """
        self.data = data if data else {}
        self.context = context

    def __getitem__(self, key, *args, **kwargs):
        try:
            # get item for data:
            ret = self.data[key]
        except KeyError as e:
            return self.generate_item(key)
        for p in self.context.data_preprocessors:
            # preprocess data ([] -> List etc)
            ret = p(ret, self.context)
        # Apply renderable data:
        if isinstance(ret, Renderable):
            ret = ret.render(self.context)
        return ret

    def generate_item(self, key):
        """ Generate item for key """
        for g in self.context.env_generators:
            try:
                ret = g(key, self.context, self.data)
                if not ret is None:
                    return ret
            except ArgumentError:
                pass
        raise KeyError('%s key is not found in translation data' % key) 

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
    return context.tr(label, context.prepare_data(data), description, options)


def submit_missed():
    return context.submit_missed()


