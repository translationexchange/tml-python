from __future__ import absolute_import
# encoding: UTF-8
from ..base import Singleton
from ..session_vars import get_current_translator

class BaseDecorator(object):

    def __init__(self, application):
        self.application = application

    def decorate(self, translated_value, translation_language, original_language, translation_key, options = {}):
        return translated_value

    def decorate_language_case(self, language_case, rule, original, transformed, options = {}):
        return transformed

    def decorate_token(self, token, value, options = {}):
        return value

    def decorate_element(self, token, value, options = {}):
        return value

    def is_inline_mode(self):
        return get_current_translator() and get_current_translator().is_inline() or False

    def enabled(self, options):
        if options.get('nowrap', False):
            return False
        return self.is_inline_mode()

    def decoration_element(self, default, options):
        if options.get('use_span', False):
            return 'span'
        if options.get('use_div', False):
            return 'div'
        return default
