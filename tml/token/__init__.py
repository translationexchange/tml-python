# encoding: UTF-8
"""
# Label tokens
#
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
from __future__ import absolute_import
import six
__author__ = 'a@toukmanov.ru'


import re
from ..exceptions import Error, RequiredArgumentIsNotPassed
from ..rules.contexts import Value
from tml.strings import to_string, suggest_string

def need_to_escape(options):
    """ Need escape string
        Args:
            options (dict): translation options
        Returns:
            boolean
    """
    if 'escape' in options:
        return options['escape']
    return True

def escape_if_needed(text, options):
    """ Escape string if it needed
        Agrs:
            text (string): text to escape
            options (dict): tranlation options (if key safe is True - do not escape)
        Returns:
            text
    """
    if hasattr(text, '__html__'):
        # Text has escape itself:
        return to_string(text.__html__())
    if need_to_escape(options):
        return escape(to_string(text))
    return to_string(text)

ESCAPE_CHARS = (('&', '&amp;'),
                ('<', '&lt;'),
                ('>', '&gt;'),
                ('"', '&quot;'),
                ("'", '&#39;'))

def escape(text):
    """ Escape text 
        Args:
            text: input text
        Returns:
            (string): escaped HTML
    """
    for find, replace in ESCAPE_CHARS:
        text = text.replace(find, replace)
    return text


class AbstractToken(object):
    """ Base token class """
    @classmethod
    def validate(self, text):
        """ Check that string is valid token
            Args:
                str (string): token string implimentation
            Returns:
                AbstractToken
        """
        raise NotImplementedError()

    def execute(self, data, options):
        """ Execute token for data with options
            data (dict): data
            options (dict): execution options
        """
        raise NotImplementedError()


class TextToken(AbstractToken):
    """ Plain text """
    def __init__(self, text):
        """ .ctor
            Args:
                text (string): token text
        """
        self.text = text

    def execute(self, data, options):
        """ Execute token 
            Returns: (string)
        """
        return self.text

    @classmethod
    def validate(cls, text, language):
        """ Validate tokenized string 
            Args:
                text(string): token text
                language (Language): token language
            Returns:
                TextToken|None
        """
        if text == '':
            # Empty text
            return TextToken(text)
        if text[0] != '{':
            return TextToken(text)


class AbstractVariableToken(AbstractToken):

    IS_VARIABLE = '([\$\d\w]+)'
    REGEXP_TOKEN = '^\{%s\}$'

    def __init__(self, name):
        self.name = name

    def fetch(self, data):
        try:
            if self.name == '$0':
                return data
            return data[self.name]
        except KeyError:
            raise RequiredArgumentIsNotPassed(self.name, data)


class VariableToken(AbstractVariableToken):
    """ Token for variabel {name} """
    # Regext to check objects
    IS_TOKEN = re.compile(AbstractVariableToken.REGEXP_TOKEN % AbstractVariableToken.IS_VARIABLE)

    def __init__(self, name):
        """
            Args:
                name (string): variable name
        """
        self.name = name

    def execute(self, data, options):
        """ Fetch and escape variable from data
            Args:
                data (dict): input data
                options (dict): translation options
            Returns:
                string
        """
        return escape_if_needed(self.fetch(data), options)

    def fetch(self, data):
        """ Fetch variable"""
        return suggest_string(super(VariableToken, self).fetch(data))


    @classmethod
    def validate(cls, text, language):
        m = cls.IS_TOKEN.match(text)
        if m:
            return VariableToken(m.group(1))

    def __str__(self):
        return '{%s}' % self.name


class RulesToken(AbstractVariableToken):
    """ 
        Token which execute some rules on variable 
        {count|token, tokens}: count = 1   -> token
                               count = 100 -> tokens 
    """
    def __init__(self, name, rules, language):
        """ .ctor
            Args:
                name (string): variable name
                rules (string): rules string
                language (Language): current language
        """
        super(RulesToken, self).__init__(name)
        self.rules = rules
        self.language = language

    TOKEN_TYPE_REGEX = '\|([^\|]{1}(.*))'
    IS_TOKEN = re.compile(AbstractVariableToken.REGEXP_TOKEN % (AbstractVariableToken.IS_VARIABLE + TOKEN_TYPE_REGEX,))
    """ Compiler for rules """
    
    @classmethod
    def validate(cls, text, language):
        m = cls.IS_TOKEN.match(text)
        if m:
            return cls(m.group(1), m.group(2), language)

    def execute(self, data, options):
        """ Execute token with var """
        return self.language.contexts.execute(self.rules, self.fetch(data)).strip()


class CaseToken(RulesToken):
    """ Language keys {name::nom} """
    IS_TOKEN = re.compile(AbstractVariableToken.REGEXP_TOKEN % (AbstractVariableToken.IS_VARIABLE + '\:\:(.*)',))

    def __init__(self, name, case, language):
        super(RulesToken, self).__init__(name)
        self.case = language.cases[str(case)]


    def execute(self, data, options):
        """ Execute with rules options """
        return escape_if_needed(
            self.case.execute(self.fetch(data)), options)


class UnsupportedCase(Error):
    def __init__(self, language, case):
        self.language = language
        self.case = case

    def __str__(self):
        return 'Language does not support case %s for locale %s' % (self.case, self.language.locale)


class PipeToken(RulesToken):
    """ 
        Token which pipe rules and join it with variable
        {count||token, tokens}: count = 1    -> 1 token
                                count = 100  -> 100 tokens
        works like {name||rules} == {name} {name|rules}
    """
    IS_TOKEN = re.compile(AbstractVariableToken.REGEXP_TOKEN % (AbstractVariableToken.IS_VARIABLE + '\|\|(.*)',))

    def __init__(self, name, rules, language):
        self.token = VariableToken(name)
        self.rules = RulesToken(name, rules, language)

    @property
    def name(self):
        return self.token.name

    def execute(self, data, options):
        """ Execute token """
        return to_string(self.token.execute(data, options))+' '+to_string(self.rules.execute(data, options))


class TokenMatcher(object):
    """ Class which select first supported token for text """
    def __init__(self, classes):
        """ .ctor
            Args:
                classes (AbstractToken.__class__[]): list of supported token classes
        """
        self.classes = classes

    def build_token(self, text, language):
        """ Build token for text - return first matched token
            Args:
                text (string): token text
            Returns:
                AbstractToken: token object
        """
        for cls in self.classes:
            ret = cls.validate(text, language)
            if ret:
                return ret
        # No token find:
        raise InvalidTokenSyntax(text)

data_matcher = TokenMatcher([TextToken, VariableToken, RulesToken, PipeToken, CaseToken])

def execute_all(tokens, data, options):
    """ Execute all tokens
        Args:
            tokens (AbstractToken[]): list of tokens
            data (dict): context
            options (dict): execution options
        Returns:
            string: executed tokens
    """
    return ''.join([to_string(token.execute(data, options)) for token in tokens])

class InvalidTokenSyntax(Error):
    """ Unsupported token syntax """
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return six.u('Token syntax is not supported for token "%s"') % self.text

