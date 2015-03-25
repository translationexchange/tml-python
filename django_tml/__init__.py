# encoding: UTF-8
from django.utils import translation
from .translator import Translator
from django.conf import settings

def tr(label, data = None, description = None, options = {}):
    return Translator.instance().context.tr(label, data, description, options)

def activate(locale):
    Translator.instance().activate(locale)

def use_source(source):
    """ Use source block
        Args:
            source (string): source name
    """
    Translator.instance().use_source(source)

def set_supports_inline_tranlation(value = True):
    """ Inline tranlations
        Args:
            value - True - enabled, False - disabled
    """
    return Translator.instance().set_supports_inline_tranlation(value)

def is_supports_inline_tranlation():
    return Translator.instance().supports_inline_tranlation

if settings.TML.get('monkeypatch', False):
    translation._trans = Translator.instance()


