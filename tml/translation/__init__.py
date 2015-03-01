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

    @property
    def client(self):
        return self.language.client


class TranslationOption(Context):
    """ Translation option with context """
    def __init__(self, label, language, context):
        """ .ctor
            Args:
                text (string): translation text
                context (dict): context rules
        """
        super(TranslationOption, self).__init__(context)
        self.tokens = default_parser.parse(label, language)
        self.language = language

    def execute(self, data, options = {}):
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


class Translation(object):
    """ Translation instance """
    def __init__(self, key, options):
        """ .ctor
            key (Key): translation key
            options (TranslationOption[]): list of translation options
        """
        self.key = key
        self.options = options

    @classmethod
    def from_data(cls, key, data):
        """ Create translation instance from API response 
            Args:
                key (Key): translated key
                data (dict[]): list of options
            Returns:
                Translation
        """
        return cls(key,
                   [TranslationOption(label= option['label'], context = option['context'] if 'context' in option else {}, language = key.language) for option in data])

    @property
    def default(self):
        """ Use key label as translation by default 
            Returns:
                TranslationOption
        """
        return TranslationOption(self.key.label, self.key.language, {})

    def execute(self, data, options):
        """ Execute translation """
        for option in self.options:
            try:
                # return result of first supported option:
                return option.execute(data, options)
            except OptionIsNotSupported:
                pass
        # by default use key label:
        return self.default.execute(data, option)

class OptionIsNotSupported(Error):
    pass