# encoding: UTF-8
from tml.token.parser import default_parser
from tml.token import execute_all
from hashlib import md5
from .context import Context
from ..exceptions import Error
from ..token.parser import default_parser


class Key(object):
    """ Translation key """
    def __init__(self, language, label, description = ''):
        """ .ctor
            Args:
                label (string): tranlated string f.ex. "{name} take me {count||apple, apples}"
                description (string): translation description
                language (Language): language instance
        """
        self.label = label
        self.description = description
        self.language = language


    @property
    def key(self):
        """ Key property """
        return md5('%s;;;%s' % (self.label, self.description)).hexdigest()

class TranslationOption(Context):
    """ Translation option with context """
    def __init__(self, text, language, rules):
        """ .ctor
            Args:
                text (string): translation text
                rules (dict): context rules
        """
        super(TranslationOption, self).__init__(rules)
        self.tokens = default_parser.parse(text, language)
        self.language = language

    def execute(self, data, options):
        """ Execute translation with given data if it is supported
            Args:
                data (dict): user data
                options (dict): exectution options
                language (language.Language): language
        """
        if not self.check(data, options, self.language):
            # Validation fault:
            raise OptionIsNotSupported(self, data, self.language)
        return execute_all(self.tokens, data, options) # execute with data


class OptionIsNotSupported(Error):
    pass