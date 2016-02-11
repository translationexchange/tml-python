from __future__ import absolute_import
# encoding: UTF-8
from tml.token.parser import default_parser
from tml.token import execute_all
from hashlib import md5
from .context import Context
from ..exceptions import Error
from ..strings import to_string
from ..token.parser import default_parser
from ..exceptions import RequiredArgumentIsNotPassed
import six


def generate_key(label, description=''):
    """Generates unique hash key for the translation key using label and description"""
    key = six.u('%s;;;%s') % (to_string(label), to_string(description))
    ret = md5(key.encode('utf-8')).hexdigest()
    return ret


class Key(object):
    """ Translation key """
    def __init__(self, language, label, description='', level=0, key=None):
        """ .ctor
            Args:
                label (string): text to be translated f.ex. "{name} take me {count||apple, apples}"
                description (string): Description of the text to be translated
                language (Language): language instance
        """
        self.label = label
        self.description = description
        self.language = language
        self.level = level
        self.key = self.build_key(key) # unique key (md5 hash) identifying this translation key

    @property
    def as_dict(self):
        return {
            'label':self.label,
            'description': self.description,
            'locale': self.locale,
            'level': self.level}

    @property
    def locale(self):
        return str(self.language.locale)

    @property
    def client(self):
        return self.language.client

    def build_key(self, key=None):
        if key is None:
            return generate_key(self.label, description=self.description)
        else:
            return key


class TranslationOption(Context):
    """ Translation option with context """
    def __init__(self, label, language, context = {}):
        """ .ctor
            Args:
                text (string): translation text
                context (dict): context rules
        """
        super(TranslationOption, self).__init__(context)
        self.label = label
        self.language = language

    def check(self, data, options):
        """ Check is option supported
            Args:
                data (dict): user data
                options (dict): execution options
            Raises:
                OptionIsNotSupported
            Returns:
                TranslationOption
        """
        if super(TranslationOption, self).check(data, options, self.language):
            return self
        else:
            raise OptionIsNotSupported(self, data, self.language)

    def execute(self, data, options = {}):
        """ Execute translation with given data if it is supported
            Args:
                data (dict): user data
                options (dict): execution options
        """
        return self.check(data, options).apply(data, options)

    def apply(self, data, options = {}):
        return execute_all(default_parser.parse(self.label, self.language), data, options) # execute with data


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

    def fetch_option(self, data, options):
        for option in self.options:
            try:
                return option.check(data, options)
            except OptionIsNotSupported:
                pass
            except RequiredArgumentIsNotPassed:
                pass
        raise OptionIsNotFound(self.key) 

    def execute(self, data, options):
        """ Execute translation """
        return self.fetch_option(data, options).execute(data, options)

    def __len__(self):
        """ Translation length """
        return len(self.options)


class NoneTranslation(Translation):
    def __init__(self, key):
        self.key = key

    def fetch_option(self, data, options):
        """ Use key label as translation by default 
            Returns:
                TranslationOption
        """
        return TranslationOption(self.key.label, self.key.language, {})


class OptionIsNotFound(Error):
    """ Translation option is not found """
    def __init__(self, key):
        self.key = key

    @property
    def label(self):
        return self.key.label

    @property
    def description(self):
        return self.key.description

    def __str__(self, *args, **kwargs):
        return 'Transaltion option not found for %s on %s' % (self.label, self.key.language.locale)

class OptionIsNotSupported(Error):
    pass