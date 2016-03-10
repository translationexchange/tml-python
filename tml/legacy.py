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

from .token.parser import default_parser
from .token import TextToken, VariableToken, RulesToken, CaseToken, PipeToken
from .rules.options import fetch_default_arg
from .strings import to_string
import re
from tml.dictionary import TranslationIsNotExists
import six


def render_token(token):
    """ Render token to sprinf """
    token_type = type(token)
    if token_type is TextToken:
        return token.text
    elif token_type is VariableToken:
        return sprintf_token(token)
    elif token_type is RulesToken:
        return fetch_default_arg(token.rules)
    elif token_type is PipeToken:
        return six.u('%s %s') % (sprintf_token(token),
                           fetch_default_arg(token.rules.rules))
    elif token_type is CaseToken:
        return sprintf_token(token)
    else:
        return six.text_type(token)


def sprintf_token(token):
    """ Convert token to sprintf syncts %(variable)s
        Args:
            token (VariableToken): token
        Returns:
            string
    """
    return '%%(%s)s' % token.name

def to_sprintf(tokens):
    """ Parse tokens and convert as printf template
        Args:
            tokens (list): list of AbstractToken
        Returns:
            string: string
    """
    return six.u('').join((render_token(token) for token in tokens))

def text_to_sprintf(text, language):
    """ Convert text with tokens to sprintf template
        Args:
            text (string): text
            language (language.Language): current language
        Returns:
            string
    """
    return to_sprintf(default_parser.parse(to_string(text), language))

LEGACY_TOKENS = re.compile('\%\((\w+?)\)s')

def suggest_label(text):
    """ Try to suggest tml label for spritnf template
        Args:
            text (string): original token
        Returns:
            string: suggested token
    """
    return re.sub(LEGACY_TOKENS, '{\\1}', text)

def translate(context, label, data, description, options):
    """ Tranlate with legacy
        Args:
            context (Context): current context
            label (str): tranlation label
            data (dict): user data
            options (dict): tranlation options
        Returns:
            text, key
    """
    translation = fetch(context, label, description)
    option = translation.fetch_option(data, options)
    # support %(name)s -> {name}
    option.label = suggest_label(option.label)
    return option.apply(data, options)

def execute(translation, data, options):
    """ Execute translation in legacy mode
        Args:
            translation (tranlation.Translation)
            data (dict): template data
            options (dict): render options
        Returns:
            string
    """
    option = translation.fetch_option(data, options)
    # support %(name)s -> {name}
    option.label = suggest_label(option.label)
    # apply translation:
    return option.apply(data, options)


def fetch(context, legacy_label, description):
    """ Fetch translation for django i18n label
        Args:
            context (context.AbstractContext): translation context
            label (string): translated label
            description (string): lalel descriptions
        Returns:
            translation.Translation
    """
    label = suggest_label(legacy_label)
    try:
        # Try to suggest translation replace %(name)s -> {name}
        # print context.dict.translations['8a7c891aa103e45e904a173f218cab9a']
        return context.fetch(label, description)
    except TranslationIsNotExists:
        return context.fallback(label, description)

