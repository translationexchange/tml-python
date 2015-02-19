# -*- coding: utf-8 -*-
from .api import allpages
from .language import LanguageError
from hashlib import md5

class TranslationKey(object):
    """ Key for translation """
    def __init__(self, label, description, language):
        """ Translations
            Args:
                label (string): translated string
                description (string): token description
                language (Language): language
        """
        self.label = label
        self.description = description
        self.language = language

    @property
    def key(self):
        return md5('%s;;;%s' % (self.label, self.description)).hexdigest()

    @property
    def url(self):
        return 'translation_keys/%s/translations/?locale=%s' % (self.key, self.language.locale)

    @property
    def translation(self):
        """ Load translation for key
            Returns:
                Translation
            Throws:
                APIError
        """
        return Translation(self, allpages(self.locale.client, self.url))


class Tranlation(object):
    """ Translation for key """
    def __init__(self, key, tranlations):
        self.key = key
        self.translations = tranlations

    def apply(self, args, context):
        return self.translations[0]

class TranslationDoesNotExists(LanguageError):
    """ Handle info about notexists tranlation """
    def __init__(self, key):
        """ .ctor
            TranslationKey key
        """
        super(TranslationDoesNotExists, self).__init__(key.language)
        self.key = key
