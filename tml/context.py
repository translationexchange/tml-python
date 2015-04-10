# encoding: UTF-8
from .application import Application
from .translation import Key
from .render import RenderEngine
from .dictionary import return_label_fallback
from .exceptions import Error
from tml.dictionary import TranslationIsNotExists
from tml.language import Language
from .dictionary import NoneDict
from .dictionary.translations import Dictionary

class ContextNotConfigured(Error):
    pass


class AbstractContext(RenderEngine):
    """ Wrapper for dictionary """
    language = None
    dict = None

    def __init__(self, language, dict, **kwargs):
        self.language = language
        self.dict = dict
        super(AbstractContext, self).__init__(**kwargs)

    def build_key(self, label, description):
        """ Build key """
        return Key(label = label, description = description, language = self.language)

    def fetch(self, label, description):
        """ Fetch Translation 
            Args:
                label (string): label
                description (string): description
            Returns:
                Translation
        """
        if self.dict:
            return self.dict.fetch(self.build_key(label, description))
        raise ContextNotConfigured(self)

    def fallback(self, label, description):
        """ Fallback translation: returns label
            Args:
                label (string)
                description (string)
            Returns:
                Translation
        """
        return self.dict.fallback(self.build_key(label, description))

    def tr(self, label, data = {}, description = '', options = {}):
        """ Tranlate data
            Args:
                label (string): tranlation label
                data (dict): user data
                description (string): tranlation description
                options (dict): options 
                language (Language):
            Returns:
                unicode
        """
        try:
            # Get transaltion:
            translation = self.fetch(label, description)
        except TranslationIsNotExists:
            # Translation does not exists: use fallback
            translation = self.fallback(label, description)
        # Render result:
        return self.render(translation, data, options)


class LanguageContext(AbstractContext):
    """ Context with selected language """
    application = None
    def __init__(self, client, locale = None, application_id = None, **kwargs):
        """ .ctor
            Args:
                client (Client): custom API client
                locale (string): selected locale
                application_id (int): API application id (use default if None)
        """
        if application_id:
            application = Application.load_by_id(client, application_id)
        else:
            application = Application.load_default(client)

        language =  Language.load_by_locale(application, 
                                            locale if locale else application.default_locale)

        super(LanguageContext, self).__init__(dict = self.build_dict(language), language = language, **kwargs)

    def build_dict(self, language):
        return Dictionary()

    _fallback_dict = None
    @property
    def fallback_dict(self):
        if not self._fallback_dict:
            if self.default_locale == self.locale:
                # Use default language:
                return NoneDict()
            self._fallback_dict = self.build_dict(self.default_language)
        return self._fallback_dict

    _default_language = None
    @property
    def default_language(self):
        if not self._default_language:
            self._default_language = Language.load_by_locale(self.application, self.default_locale)
        return self._default_language

    @property
    def default_locale(self):
        return self.language.application.default_locale

    @property
    def locale(self):
        return self.language.locale

    @property
    def application(self):
        return self.language.application

    def fallback(self, label, description):
        """ Fallback translation: try to use default language """
        try:
            return self.fallback_dict.fetch(Key(label = label,
                                                description = description,
                                                language = self.default_language))
        except TranslationIsNotExists:
            return super(LanguageContext, self).fallback(label, description)

