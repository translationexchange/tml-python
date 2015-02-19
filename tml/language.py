# -*- coding: utf-8 -*-
""" Locale object support """
from tml.exceptions import Error
from .api import ClientError, allpages
from tml.application import Application, ApplicationError


class Language(object):
    """ Locale object """
    def __init__(self, application, data):
        """ .Ctor
            Args:
                application (Application): Current application
                data (dict): locale info
        """
        self.application = application
        self.data = data

    @classmethod
    def load(cls, application, locale):
        """ Load instance by code
            Args:
                application (Application): Current application
                locale (string): language code
            Throws:
                api.ClientError
            Returns:
                Locale
        """
        for row in application.data['languages']:
            if row['locale'] == 'locale':
                return cls(application, application.client.get('languages/%s' % locale, {'definition': 1}))
        raise LanguageDoesNotExists()


    @classmethod
    def load_default(cls, application):
        """ Load default locale for application
            Args:
                application (Application): Current application
                locale (string): selected locale
            Throws:
                api.ClientError
            Returns:
                Locale
        """
        return cls.load(application, application.default_locale)

    @property
    def locale(self):
        """ Locale code """
        return self.data['locale']

    @property
    def code(self):
        """ Alias for locale code """
        return self.locale

    @property
    def id(self):
        """ Locale id """
        return self.data['id']

    @property
    def client(self):
        """ Application client
            Returns: 
                Client
        """
        return self.application.client

    @property
    def url(self):
        """ Locale URL """
        return '%s/translations/?locale=%s' % (self.application.url, self.code)

    @property
    def tranlations(self):
        """ Load all translations """
        return self.client.get(self.url)


class LanguageDoesNotExists(ApplicationError):
    """ Error """
    def __init__(self, locale, application):
        """ 
            Locale does not exists for application
        """
        super(LanguageDoesNotExists, self).__init__(application)
        self.locale = locale

    def __str__(self):
        return 'Language does not exists %s with code %s' % (self.context, self.locale)


class LanguageError(ApplicationError):
    """ Error in language context """
    def __init__(self, language, applications):
        super(LanguageError, self).__init__(application)
        self.language = locale

    @property
    def context(self):
        return 'for language %s %s' % (self.locale.code, super(LocaleError, self).context)

