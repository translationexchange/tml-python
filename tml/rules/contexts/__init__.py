# encoding: UTF-8
""" Rules variables, like @gender, @n """
from tml.exceptions import Error as BaseError
from _ctypes import ArgumentError
from .count import Count
from .number import Number
from .date import Date
from .gender import Gender
from .genders import Genders
from ..options import Parser as OptionsParser
from tml.rules.options import TokenMapping
from tml.rules import Case as RulesCase
from distutils.command.config import config


class Value(object):
    """ Value contexts """
    @classmethod
    def match(cls, data):
        return str(data)

    def __call___(self, data):
        return self.match(data)


class UnsupportedContext(BaseError):
    pass


SUPPORTED_CONTEXTS = [('date', Date),
                      ('gender', Gender),
                      ('genders', Genders),
                      ('list', Count),
                      ('number', Number),
                      ('value', Value)]

class Context(object):
    """ Variable context """
    def __init__(self, pattern, options_parser, rules, variable_name):
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
        except ArgumentError as e:
            raise UnsupportedContext(self, e)
        # execute rules for tokens, get a key for data:
        return self.rules.apply(data)

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
        return self.options_parser.parse(token_options)[self.option(value)]


class Contexts(object):
    """ List of contexts """
    def __init__(self, contexts):
        """ .ctor
            Args:
                contexts (Context[])
        """
        if not all([isinstance(el, Context) for el in contexts]):
            # Check that any element is context:
            raise ArgumentError('Contexts list contains not context object', contexts)
        self.contexts = contexts

    def execute(self, token_options, value):
        """ Execute token options for value at firs supported context
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
        raise ArgumentError('Could not detect context for object %s' % value, value)

    def option(self, value):
        """ Get context option for given value """
        for context in self.contexts:
            try:
                return context.option(value)
            except UnsupportedContext:
                pass
        raise ArgumentError('Could not detect context for object %s' % value, value)

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
                data = config[key]
            except KeyError:
                # context is not defined in config
                continue
            ret.contexts.append(Context(pattern,
                                        OptionsParser(data['keys'],
                                                     data['default_key'],
                                                     TokenMapping.build(data['token_mapping'])),
                                        RulesCase.from_rules(data['rules'], data['default_key']),
                                        data['variables'][0][:1]))
        return ret


