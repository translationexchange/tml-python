# encoding: UTF-8
from django.utils import translation
from .translator import Translator
from django.conf import settings

def tr(label, data = None, description = None, options = {}):
    return Translator.instance().context.tr(label, data, description, options)

def activate(locale):
    Translator.instance().activate(locale)

if settings.TML.get('monkeypatch', False):
    translation._trans = Translator.instance()
    _supported = [(lang['locale'], lang['native_name']) for lang in translation._trans.default.application.languages]

