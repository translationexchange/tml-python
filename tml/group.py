""" Groups - tools for mass load translations """
from .translation import TranslationKey, Translation, TranslationDoesNotExists

class Group(object):
    """ Group based on language """
    def __init__(self, translations):
        """ .ctor
            Args:
                translations (hash): dict with translations
        """
        self.translations = translations

    def tranlate(self, key):
        """ Tranlate key
            Args:
                label (string): translated string
                description (string): token description
            Returns:
                Translation
            Throws:
                TranslationDoesNotExists
        """
        key = TranslationKey(label, description, self.language)
        try:
            return Translation(key, self.tranlations[key.key])
        except KeyError:
            raise TranslationDoesNotExists(key)

class NullGroup(object):
    """ Stub for group """
    def translate(self, key):
        """ Just load tranlation """
        return Translation.load(key)

class LanguageGroup(object):
    """ Preload all translations for language and works as group """
    def __init__(self, language):
        self.language = language
        super(LanguageGroup, self).__init__(language.translations)

