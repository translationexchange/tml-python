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
from __future__ import absolute_import
import six
from argparse import ArgumentError
from tml.dictionary import TranslationIsNotExists
from .decoration.parser import parse as decoration_parser
from .tools import Renderable
from .translation import OptionIsNotFound
from .tools import BasePreprocessor


class RenderEngine(object):
    """ Engine to render translations """
    # List of objects which preprocess data before translation
    # (join lists for example)
    data_preprocessors = []
    # List of objects which add custom values to data (like viewing_user)
    env_generators = []

    def render(self, translation, data, options=None, fallback = False):
        """ Render translation
            Args:
                translation (Transaltion): translation to render
                data (dict): user data
                options (dict): transaltion options
            Returns:
                unicode
        """
        # Wrap data:
        options = {} if options is None else options
        translation_data = self.prepare_data(data)
        try:
            option = translation.fetch_option(translation_data, options)
        except OptionIsNotFound as e:
            translation = self.fallback(e.label, e.description)
            option = translation.fetch_option(translation_data, options)
        trans_value = decoration_parser(option.execute(translation_data, options)).render(translation_data)
        trans_options = option.get_options()
        trans_options.update(options)
        return self.wrap_to_tml(translation.key, trans_value, self.language, trans_options)

    def wrap_to_tml(self, key, translated_value, target_language, translation_options):
        """
            translation_options
                locked - bool flag, if translation option marked as locked
                pending - bool flag, indicates that translation is either registering or there is no options.
                locale - locale string, used to check whether string used fallback or translated labels
        """
        if not self.wrap_enabled(translation_options):
            return translated_value
        if self.application.feature_enabled('lock_original_content') and self.default_language == target_language:
            return translated_value
        classes = set(['tml_translatable'])
        if translation_options.get('locked', False):
            classes.add('tml_locked')
        elif 'pending' in translation_options:
            classes.add('tml_pending' if translation_options['pending'] else 'tml_not_translated')
        else:
            if 'locale' in translation_options:
                if translation_options['locale'] != target_language.locale:
                    classes.add('tml_fallback')
                else:
                    classes.add('tml_translated')
        element = self.decoration_element('tml:label', translation_options)
        context = {
            'element': element,
            'class_name': " ".join(classes),
            'key': key.key,
            'locale': target_language.locale,
            'text': translated_value}
        return six.u('<%(element)s class="%(class_name)s" data-translation_key="%(key)s" data-target_locale="%(locale)s">%(text)s</%(element)s>') % context   # temporary

    def wrap_enabled(self, options):
        if options.get('nowrap', False):
            return False
        return self.is_inline_mode()

    def decoration_element(self, default, options):
        if options.get('use_span', False):
            return 'span'
        if options.get('use_div', False):
            return 'div'
        return default

    def fallback(self, label, description):
        raise NotImplemented('Fallback is not implemented for context')

    def prepare_data(self, data):
        """ Render engine """
        return Data(data, self)


class Data(object):
    """ Some data can be prerendered with current context """
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
        except KeyError:
            return self.generate_item(key)
        for preprocessor in self.context.data_preprocessors:
            # preprocess data ([] -> List etc)
            if type(preprocessor) is type:
                if isinstance(preprocessor, BasePreprocessor):
                    ret = preprocessor(ret, self.data).process()
            else:
                ret = preprocessor(ret, self.data)
        # Apply renderable data:
        if isinstance(ret, Renderable):
            ret = ret.render(self.context)
        return ret

    def generate_item(self, key):
        """ Generate item for key """
        for generator in self.context.env_generators:
            try:
                ret = generator(key, self.context, self.data)
                if not ret is None:
                    return ret
            except ArgumentError:
                pass
        raise KeyError('%s key is not found in translation data' % key)

