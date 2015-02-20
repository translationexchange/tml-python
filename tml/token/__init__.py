# encoding: UTF-8
import re
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
        if text == '':
            # Empty text
            return TextToken(text)
        if text[0]!='{':
            return TextToken(text)

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

class TokenMatcher(object):
    """ Class which select first supported token for text """
    def __init__(self, classes):
        """ .ctor
            Args:
                classes (AbstractToken.__class__[]): list of supported token classes
        """
        self.classes = classes

    def build_token(self, text):
        """ Build token for text - return first matched token
            Args:
                text (string): token text
            Returns:
                AbstractToken: token object
        """
        for cls in self.classes:
            ret = cls.validate(text)
            if ret:
                return ret
        # No token find:
        raise InvalidTokenSyntax(text)

def execute_all(tokens, data, options):
    """ Execute all tokens
        Args:
            tokens (AbstractToken[]): list of tokens
            data (dict): context
            options (dict): execution options
        Returns:
            string: executed tokens
    """
    return ''.join([token.execute(data, options) for token in tokens])

class InvalidTokenSyntax(Error):
    """ Unsupported token syntax """
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return u'Token syntax is not supported for token "%s"' % self.text
