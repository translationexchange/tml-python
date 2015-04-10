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
from .dictionary import AbstractDictionary
from .context import LanguageContext, ContextNotConfigured


__author__ = 'a@toukmanov.ru'


class Context(LanguageContext):
    """ Execution context """

    def __init__(self, token = None, source = None, client = None, missed_keys = None, **kwargs):
        """ Configure tranlation
            Args:
                token (string): API token
                locale (string): selected locale
                application_id (int): API application id (use default if None)
                client (Client): custom API client
                decoration_tags (TagsFactory): custom decoration tags
                use_fallback_dictionary (Boolean): use fallback dictionart
        """
        self.source = source
        super(Context, self).__init__(client = client if client else Client(token), **kwargs)
        self.missed_keys = missed_keys

    def build_dict(self, language):
        """ Build dictionary for language """
        if self.source:
            return SourceDictionary(self.source, language)
        return super(Context, self).build_dict(language)

    def submit_missed(self):
        """ Submit missed key to server after app is executed """
        if self.missed_keys is None:
            raise ContextNotConfigured('Translation is not configured')
        self.missed_keys.submit_all()


context = None

def configure(**kwargs):
    global context
    context = Context(**kwargs)

def get_context():
    global context
    if not context:
        raise ContextNotConfigured()
    return context

def tr(label, data = {}, description = '', options = {}):
    """ Tranlate data
        Args:
            label (string): tranlation label
            data (dict): user data
            description (string): tranlation description
            language (Language):
            options (dict): options 
    """
    return get_context().tr(label, context.prepare_data(data), description, options)


def submit_missed():
    return get_context().submit_missed()


