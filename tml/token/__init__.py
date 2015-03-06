# encoding: UTF-8
import re
from ..exceptions import Error, RequiredArgumentIsNotPassed
from ..rules.contexts import Value

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
        if text[0]!='{':
            return TextToken(text)


class AbstractVariableToken(AbstractToken):
    def __init__(self, name):
        self.name = name

    def fetch(self, data):
        try:
            return data[self.name]
        except KeyError:
            raise RequiredArgumentIsNotPassed(self.name, data)


class VariableToken(AbstractVariableToken):
    """ Token for variabel {name} """
    USE_KEYS = ['name','title','text'] # Keys in dict to fetch printable value
    IS_TOKEN = re.compile('\{(\w+)\}') # Regext to check objects
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
        return self.escape_if_needed(Value.match(self.fetch(data)), options)

    def escape_if_needed(self, text, options):
        """ Escape string if it needed
            Agrs:
                text (string): text to escape
                options (dict): tranlation options (if key safe is True - do not escape)
            Returns:
                text
        """
        text = text.encode('utf-8')
        if self.need_to_escape(options):
            return self.escape(text)
        return text

    def escape(self, text):
        """ Escape text 
            Args:
                text: input text
            Returns:
                (string): escaped HTML
        """
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

    def need_to_escape(self, options):
        """ Need escape string
            Args:
                options (dict): translation options
            Returns:
                boolean
        """
        try:
            # Use "safe" option to not escape valiable data:
            return not options['safe']
        except KeyError:
            # Escape by default:
            return True

    @classmethod
    def validate(cls, text, language):
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

    IS_TOKEN = re.compile('^\{(\w+)\|([^\|]{1}(.*))\}$')
    """ Compiler for rules """
    @classmethod
    def validate(cls, text, language):
        m = cls.IS_TOKEN.match(text)
        if m:
            return cls(m.group(1), m.group(2), language)

    def execute(self, data, options):
        """ Execute token with var """
        return self.language.contexts.execute(self.rules, self.fetch(data))

class CaseToken(RulesToken):
    """ Language keys {name::nom} """
    IS_TOKEN = re.compile('^\{(\w+)\:\:(.*)\}$')

    def __init__(self, name, case, language):
        super(RulesToken, self).__init__(name)
        self.case = language.cases[case]


    def execute(self, data, options):
        """ Execute with rules options """
        return self.escape_if_needed(self.case.execute(self.fetch(data)), options)


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
    IS_TOKEN = re.compile('^\{(\w+)\|\|(.*)\}$')

    def __init__(self, name, rules, language):
        self.token = VariableToken(name)
        self.rules = RulesToken(name, rules, language)

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
    return ''.join([token.execute(data, options) for token in tokens])

class InvalidTokenSyntax(Error):
    """ Unsupported token syntax """
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return u'Token syntax is not supported for token "%s"' % self.text

