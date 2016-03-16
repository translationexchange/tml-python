# encoding: UTF-8
"""
# Token options: parsing and mapping
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
import re
from six.moves import range
from tml.session_vars import get_current_context
from tml.exceptions import Error as BaseError
from ..strings import to_string


__author__ = 'xepa4ep, a@toukmanov.ru'


def is_language_cases_enabled():
    context = get_current_context()
    if not context:
        return False
    if not context.application:
        return False
    return context.application.feature_enabled('language_cases')


class TokenMapping(object):
    """ Class which maps list of args to assoc args"""

    UNSUPPORTED = 'unsupported'

    def __init__(self, mapping):
        """ .ctor
            mapping (dict): key - mapped argument name, value - expression to fetch from args
        """
        self.mapping = mapping

    def apply(self, args):
        """ Apply mapping
            Args:
                args (list): list of arguments
            Returns:
                dict: kwargs mapped by rules
        """
        ret = {}
        context = get_current_context()
        for key in self.mapping:
            ret[key] = apply_mapping_rule(self.mapping[key], args)
        return ret

    @classmethod
    def build(cls, settings):
        """ Build a mapping from arguments
            Args:
                settings (list): list of settings, each element is a mapping dict or "unsupported" string
            Returns:
                TokenMapping[]
        """
        ret = {}
        for i in range(len(settings)):
            if settings[i] != cls.UNSUPPORTED:
                ret[i] = TokenMapping(settings[i])
        return ret


class Error(BaseError):
    """ Abstract options parse error """
    def __init__(self, rule, msg=None):
        super(Error, self).__init__()
        self.rule = rule
        self.msg = msg

    def __str__(self):
        return self.msg


IS_KWARG = re.compile('^(\w+)\s*\:(.*)$')
SCAN_VALUE = re.compile('({\$(\d+)(::\w+)*})')

def apply_mapping_rule(rule, args):
    """ Apply mapping rule on args
        Args:
            rule (string): string rule where ${\d+} is replaced with argument value with expression index
            args (list): list of args
    """
    rule = to_string(rule)
    value = rule  # {$0::plural}

    for group in SCAN_VALUE.findall(rule):
        token = group[0]
        var_idx, cases = int(group[1]), []
        if len(args) < var_idx:  # $5, but there is only 2 args ['message', 'messages']
            raise IndexOutOfBounds(rule)
        token_value = args[var_idx]
        value = value.replace(token, token_value)
        if len(group) > 2:
            value += group[2]
    return value


def parse_args(text):
    """ Fetch arges from text
        Args:
            text (string): list of args
        Returns:
            (list, dict): list of not named args and dict with named args
    """
    kwargs = {}
    args = []
    for part in text.split(','):
        key, value = parse_kwarg(part)
        if key is None:
            args.append(value)
        else:
            kwargs[key] = value

    return (args, kwargs)

def fetch_default_arg(text):
    """ Fetch default argument from rule
        Args:
            text (string): list of options a,b,c or a:value1,b:value2
        Returns:
            string: first value (a or value1)
    """
    return parse_kwarg(text.split(',')[-1])[1]

def parse_kwarg(part):
    """ Parse kwarg:
        Args:
            part (string): expression like key:value or just value
        Returns:
            tuple (key, value)
    """
    part = to_string(part).strip(' ')
    match = IS_KWARG.match(part)
    if match:
        return (match.group(1).strip(' '), match.group(2).strip(' '))
    else:
        return (None, part)

class Parser(object):
    """ Parser for options """
    def __init__(self, keys, default_key, token_mapping):
        """ .ctor
            keys (list): list of keys
            token_mapping (TokenMapping[]): list of token mappings
            default_key (string): default
        """
        self.keys = keys
        self.default_key = default_key
        self.token_mapping = token_mapping

    def parse(self, text):
        """ Parse argument string
            Args:
                text (string): argument
                                named e.c. one: argument, many: arguments
                                list e.c argument, arguments
        """
        (args, kwargs) = parse_args(text)
        if len(kwargs) and len(args):
            # Not parse mixed args like one: argument, arguemnts
            raise MixOfNamedAndOrderedArgs(text)
        if len(args):
            # Only args:
            return self.apply_token_mapping(args, text)
        # Only kwargs:
        return self.validate_kwargs(kwargs, text)

    def apply_token_mapping(self, args, text):
        """ Apply token mapping on args
            Args:
                args (list): list of arguments
                text (string): original expression (for exception)
            Raises:
                InvalidNumberOfArguments
            Returns:
                dict
        """
        if len(args):
            try:
                return self.token_mapping[len(args) - 1].apply(args)
            except KeyError:
                raise  InvalidNumberOfArguments(text)

    def validate_kwargs(self, kwargs, text):
        """ Validate parsed kwargs
            Args:
                kwargs (dict): kwargs list
                text (string): original expression
            Throws:
                UnsupportedKey: kwargs contains unknown key
                MissedKey(
            Returns:
                dict
        """
        for key in kwargs:
            # Check is kwargs supported:
            if not key in self.keys:
                raise UnsupportedKey(key, text)
        # Check is default_key presents:
        try:
            default = kwargs[self.default_key]
        except KeyError:
            raise MissedKey(self.default_key, text)
        # Replace all missed keys with default:
        for key in self.keys:
            if not key in kwargs:
                kwargs[key] = default
        return kwargs


class MixOfNamedAndOrderedArgs(Error):
    """ Options contains args and kwargs both """
    pass


class UnsupportedKey(Error):
    """ List of tokens contains unsuppoted key """
    def __init__(self, key, rule):
        super(UnsupportedKey, self).__init__(rule)
        self.key = key

    MESSAGE = 'Rule contains unsupported key %s in expression "%s"'
    def __str__(self, *args, **kwargs):
        return self.MESSAGE % (self.key, self.rule)


class MissedKey(Error):
    """ Required key is missed """
    def __init__(self, key, rule):
        """ .ctor
            Args:
                key (string): missed key name
                rule (string): rule string
        """
        super(MissedKey, self).__init__(rule)
        self.key = key

    MESSAGE = 'Rule does not contains key "%s" in expression "%s"'
    def __str__(self):
        return self.MESSAGE % (self.key, self.rule)

class InvalidNumberOfArguments(Error):
    """ Args parser error """

    def __str__(self, *args, **kwargs):
        return 'Unsupported arguments count in expression "%s"' % (self.rule)

    def apply(self):
        """ Apply exception
            Raises:
                InvalidNumberOfArguments
        """
        raise self


class IndexOutOfBounds(Error):

    def __str__(self, *args, **kwargs):
        return "The index inside `%s` is out of bounds" % self.rule
