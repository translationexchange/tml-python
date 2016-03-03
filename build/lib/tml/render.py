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

from .decoration.parser import parse as decoration_parser
from .tools import Renderable
from argparse import ArgumentError
from tml.dictionary import TranslationIsNotExists
from .translation import OptionIsNotFound
from .tools import BasePreprocessor


class RenderEngine(object):
    """ Engine to render translations """
    # List of objects which preprocess data before translation
    # (join lists for example)
    data_preprocessors = []
    # List of objects which add custom values to data (like viewing_user)
    env_generators = []

    def render(self, translation, data, options, fallback = False):
        """ Render translation
            Args:
                translation (Transaltion): translation to render
                data (dict): user data
                options (dict): transaltion options
            Returns:
                unicode
        """
        # Wrap data:
        translation_data = self.prepare_data(data)
        try:
            # Apply tokens:
            ret = translation.execute(translation_data, options)
        except OptionIsNotFound as e:
            # Option does not exists for data, use fallback translation:
            translation = self.fallback(e.label, e.description)
            ret = translation.execute(translation_data, options)
        # Apply decoration:
        return decoration_parser(ret).render(translation_data)

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

