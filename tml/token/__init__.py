# encoding: UTF-8
import re
from django.template.base import Token
from ..exceptions import Error 

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
    def validate(cls, text):
        """ Validate tokenized string """
        if text[0]!='{':
            return TextToken(str)

class VariableToken(AbstractToken):
    """ Token for variabel {name} """
    def __init__(self, name):
        self.name = name

    def execute(self, data, options):
        return unicode(data[self.name])

    IS_TOKEN = re.compile('\{(\w+)\}')
    @classmethod
    def validate(cls, text):
        m = cls.IS_TOKEN.match(text)
        if m:
            return VariableToken(m.group(1))

    def __str__(self):
        return '{%s}' % self.name

class RulesToken(VariableToken):
    """ 
        Token which execute some rules on variable 
        {count|token, tokens}: count = 1   -> token
                               count = 100 -> tokens 
    """
    def __init__(self, name, rules):
        """ .ctor
            Args:
                name (string): variable name
                rules (string): rules string
        """
        super(RulesToken, self).__init__(name)
        self.rules = rules

    IS_TOKEN = re.compile('^\{(\w+)\|([^\|]{1}(.*))\}$')
    """ Compiler for rules """
    rules_compiller = None
    @classmethod
    def validate(cls, text):
        m = cls.IS_TOKEN.match(text)
        if m:
            return cls(m.group(1), m.group(2))

    def execute(self, data, options):
        """ Execute token with var """
        return RulesToken.rules_compiller.compile(self, data[self.name], options).execute()

class PipeToken(RulesToken):
    """ 
        Token which pipe rules and join it with variable
        {count||token, tokens}: count = 1    -> 1 token
                                count = 100  -> 100 tokens
        works like {name||rules} == {name} {name|rules}
    """
    IS_TOKEN = re.compile('^\{(\w+)\|\|(.*)\}$')

    def __init__(self, name, rules):
        self.token = VariableToken(name)
        self.rules = RulesToken(name, rules)

    def execute(self, data, options):
        """ Execute token """
        return '%s %s' % (self.token.execute(data, options), self.rules.execute(data, options))

