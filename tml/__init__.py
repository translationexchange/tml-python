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
from .context import (LanguageContext,
                      ContextNotConfigured,
                      SourceContext,
                      SnapshotContext)
from .api.snapshot import open_snapshot
from .render import RenderEngine
from .utils import enable_warnings

__author__ = 'a@toukmanov.ru'


def build_client(client, snapshot_path, token):
    """ Client builder 
        Args:
            client (api.client.Client): custom client
            snapshot_path (string): path to snapshot (returns SnapshotClient)
            token (string): API token
        Returns:
            api.client.Client: client
    """
    if client:
        # Client instance passed:
        return client
    elif snapshot_path:
        # Get data from snapshot:
        return open_snapshot(snapshot_path)
    # Get data from API:
    return Client(token)

def build_context(token = None,
                  source = None,
                  client = None,
                  snapshot_path = None,
                  use_snapshot = False,
                  **kwargs):
    """ Build context for settings
        Args:
            token (string): API access token
            source (string): source name
            client (api.client.Client): custom client
            snapshot_path (string): path to snapshot file
            use_snapshot (boolean): flag for snapshot usagr
        Returns:
            tml.context.AbstractContext: context instance
    """
    kwargs['client'] = build_client(client, snapshot_path, token)
    if use_snapshot:
        return SnapshotContext(source, **kwargs)
    if source:
        return SourceContext(source, **kwargs)
    else:
        return LanguageContext(**kwargs)

DEFAULT_CONTEXT = None

def configure(**kwargs):
    """ Build context and set as default """
    global DEFAULT_CONTEXT
    DEFAULT_CONTEXT = build_context(**kwargs)
    enable_warnings()

def get_context():
    """ Get current context """
    if not DEFAULT_CONTEXT:
        raise ContextNotConfigured()
    return DEFAULT_CONTEXT

def tr(label, data = {}, description = '', options = {}):
    """ Tranlate data
        Args:
            label (string): tranlation label
            data (dict): user data
            description (string): tranlation description
            language (Language):
            options (dict): options 
    """
    context = get_context()
    return context.tr(
        label,
        context.prepare_data(data),
        description,
        options)


