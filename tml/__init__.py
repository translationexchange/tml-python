# encoding: UTF-8
from .exceptions import Error
from .application import Application
from .language import Language
from .api.client import Client
from .dictionary import Hashtable, TranslationIsNotExists
from .dictionary.translations import Dictionary
from .dictionary.source import SourceDictionary
from .translation import Key
from .rules.contexts.gender import Gender
from .decoration import system_tags as system_decoration_tags
from .dictionary import AbstractDictionary
from .context import LanguageContext, ContextNotConfigured, SourceContext, SnapshotContext
from .api.snapshot import open_snapshot
from render import RenderEngine

__author__ = 'a@toukmanov.ru'


def build_client(client, snapshot_path, token):
    if client:
        # Client instance passed:
        return client
    elif snapshot_path:
        # Get data from snapshot:
        return open_snapshot(snapshot_path)
    # Get data from API:
    return Client(token)

def build_context(token = None, source = None, client = None, snapshot_path = None, use_snapshot = False, **kwargs):
    kwargs['client'] = build_client(client, snapshot_path, token)
    if use_snapshot:
        return SnapshotContext(source, **kwargs)
    if source:
        return SourceContext(source, **kwargs)
    else:
        return LanguageContext(**kwargs)

context = None

def configure(**kwargs):
    global context
    context = build_context(**kwargs)

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


