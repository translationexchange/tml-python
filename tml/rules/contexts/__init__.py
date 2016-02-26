# encoding: UTF-8
"""
# Rules variables, like @gender, @n
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
__author__ = 'a@toukmanov.ru, xepa4ep'

import re
from tml.exceptions import Error as BaseError
from _ctypes import ArgumentError
from .count import Count
from .number import Number
from .date import Date
from .gender import Gender
from .genders import Genders
from ..options import Parser as OptionsParser
from tml.rules.options import TokenMapping
from tml.rules import ContextRules
from ...exceptions import Error
from ...strings import to_string, suggest_string

class Value(object):
    """ Value contexts """

    @classmethod
    def match(cls, data):
        """ Data is value """
        return to_string(suggest_string(data))

    def __call___(self, data):
        return self.match(data)


class UnsupportedContext(BaseError):
    """ Base error for context """
    pass


class ValueIsNotMatchContext(UnsupportedContext):
    """ Raises when try to fetch option for invalid value """
    def __init__(self, error, context, value):
        """ .ctor
            Args:
                error (Exception): why value does not supports context
                context (Context): context instance
                value (mixed): value
        """
        super(ValueIsNotMatchContext, self).__init__()
        self.error = error
        self.context = context
        self.value = value

    MESSAGE = 'Value is not match context %s. Unsupported %s "%s"'

    def __str__(self, *args, **kwargs):
        return self.MESSAGE % (str(self.context),
                               type(self.value).__name__,
                               self.value)


SUPPORTED_CONTEXTS = [('date', Date),
                      ('gender', Gender),
                      ('genders', Genders),
                      ('list', Count),
                      ('number', Number),
                      ('variables', Value)]

class Context(object):
    """ Variable context """
    def __init__(self, pattern, options_parser, rules, variable_name, token_expression=None):
        """ .ctor
            pattern (Value): pattern for variable token
            options_parser (OptionsParser): parser for token options
            rules (tml.rules.Case): rules to detect what options is
            variable_name (string): name of variable for rules
        """
        self.pattern = pattern
        self.options_parser = options_parser
        self.rules = rules
        self.variable_name = variable_name
        if token_expression:
            self.token_expression = re.compile(token_expression[1:-2])

    def applies_to_token(self, token):
        """Check whether this token applies to context"""
        if not self.token_expression:
            return False
        return self.token_expression.match(token) is not None

    def match(self, value):
        """ Check is value match context
            Args:
                value: mixed data
            Raises:
                AgrumentError: value does not match context
            Returns:
                normalized data for context
        """
        return self.pattern.match(value)

    def option(self, value):
        """ Get option for value
            Args:
                value: mixed data
            Raises:
                UnsupportedContext: value does not match context
            Returns:
                string: option after rules apply
        """
        # check context for value:
        try:
            data = {self.variable_name: self.match(value)}
        except ArgumentError as not_match:
            raise ValueIsNotMatchContext(error = not_match,
                                         context = self,
                                         value = value)
        # execute rules for tokens, get a key for data:
        return self.rules.apply(data)

    def __str__(self):
        return self.pattern.__name__

    def execute(self, token_options, value):
        """ Execute context for value with options
            Args:
                token_options (string): token options like 'male: he, female: she, default: it'
                value (mixed): value
                options (dict): parser options
            Raises:
                AgrumentError: value does not match context
            Returns:
                string: token value after rules applyes
        """
        # return option:
        option = self.option(value)
        return self.options_parser.parse(token_options)[option]

    @classmethod
    def from_data(cls, data, pattern):
        """ Build context from API response
            Args:
                data (dict): API data
                pattern (Value): pattern for variable token
            Returns:
                context
        """
        return Context(pattern,
                       OptionsParser(data['keys'],
                                     data['default_key'],
                                     TokenMapping.build(data['token_mapping'])),
                       ContextRules.from_rules(data['rules'],
                                               data['default_key']),
                       data['variables'][0][1:],
                       data.get('token_expression', None))


class Contexts(object):
    """ List of contexts """
    def __init__(self, contexts, index = {}):
        """ .ctor
            Args:
                contexts (Context[])
                index (dict): search index (key - context code, value - context index)
        """
        if not all([isinstance(el, Context) for el in contexts]):
            # Check that any element is context:
            raise ArgumentError('Contexts list contains not context object',
                                contexts)
        self.contexts = contexts
        self.index = index


    def execute(self, token_options, value):
        """ Execute token options for value at first supported context
            Args:
                token_options (string): token options as 'he, she, it'
                value: token value
            Returns:
                string
        """
        for context in self.contexts:
            try:
                return context.execute(token_options, value)
            except UnsupportedContext:
                pass
        raise ArgumentError('Could not detect context for object %s' % value,
                            value)

    def option(self, value):
        """ Get context option for given value """
        for context in self.contexts:
            try:
                return context.option(value)
            except UnsupportedContext:
                pass
        raise ArgumentError('Could not detect context for object %s' % value,
                            value)

    def find_by_code(self, code):
        """ Find context by code
            Args:
                code (string)
            Raises:
                KeyError (context not found)
            Returns:
                Context
        """
        try:
            return self.contexts[self.index[code]]
        except KeyError:
            raise ContextNotFound(code, self)

    def find_by_token_name(self, token):
        """Find context by token using regex matching rules"""
        search_iter = (context for context in
                       self.contexts if context.applies_to_token(token))
        try:
            return next(search_iter)
        except StopIteration:
            raise ContextNotFound(token, self)

    @classmethod
    def from_dict(cls, config):
        """ Build context from API response
            Args:
                config (dict): API response by key contexts
            Return:
                Contexts
        """
        ret = cls([])
        for key, pattern in SUPPORTED_CONTEXTS:
            # Use only supported context in define order:
            try:
                ret.contexts.append(Context.from_data(config[key], pattern))
                ret.index[key] = len(ret.contexts)-1
            except KeyError:
                # context is not defined in config
                continue

        return ret


class ContextNotFound(Error):
    """ Invalid context code """
    def __init__(self, code, contexts):
        super(ContextNotFound, self).__init__()
        self.code = code
        self.contexts = contexts

    def __str__(self, *args, **kwargs):
        return 'Context \'%s\' not supported' % self.code

