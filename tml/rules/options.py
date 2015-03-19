# encoding: UTF-8
""" Tools for parse tokens mapping """
from tml.exceptions import Error as BaseError
import re


class TokenMapping(object):
    """ Class which maps list of args to assoc args"""
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
        for key in self.mapping:
            ret[key] = apply_mapping_rule(self.mapping[key], args)

        return ret

    UNSUPPORTED = 'unsupported'

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
    def __init__(self, rule):
        self.rule = rule


def apply_mapping_rule(rule, args):
    """ Apply mapping rule on args 
        Args:
            rule (string): string rule where ${\d+} is replaced with argument value with expression index
            args (list): list of args
    """
    i = 0
    rule = rule.encode('utf-8')
    for arg in args:
        rule = rule.replace('{$%d}' % i, arg)
        i = i + 1
    return rule


IS_KWARG = re.compile('^(\w+)\s*\:(.*)$')


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
            args.append(part)
        else:
            kwargs[key] = value

    return (args, kwargs)

def fetch_default_arg(text):
    return parse_kwarg(text.split(',')[-1])[1]

def parse_kwarg(part):
    m = IS_KWARG.match(part)
    if m:
        return (m.group(1), m.group(2).strip())
    else:
        return (None, part.strip())

class Parser(object):
    """ Parser for options """
    def __init__(self, keys, default_key, token_mapping):
        """ .ctor
            rules (list): list of rules
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
                raise  InvalidNumberOfArguments(len(args), text)
    
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
    pass


class UnsupportedKey(Error):
    """ List of tokens contains unsuppoted key """
    def __init__(self, key, rule):
        super(UnsupportedKey, self).__init__(rule)
        self.key = key

    def __str__(self, *args, **kwargs):
        return 'Rule contains unsupported key %s in expression "%s"' % (self.key, self.rule)


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

    def __str__(self):
        return 'Rule does not contains key "%s" in expression "%s"' % (self.key, self.rule)

class InvalidNumberOfArguments(Error):
    """ Args parser error """
    def __init__(self, text, arguments_count):
        """ Invalid arguments count
            Args:
                text (string): expression
                argument_count: unsupported argument count
        """
        super(InvalidNumberOfArguments, self).__init__(text)
        self.arguments_count = arguments_count

    def __str__(self, *args, **kwargs):
        return 'Unsupported arguments count in expression "%s"'

    def apply(self, args):
        raise self
