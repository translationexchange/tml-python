# encoding: UTF-8
__author__ = 'a@toukmanov.ru'

from .exceptions import Error

class Application(object):
    """ TML application """
    def __init__(self, client, id, languages, default_locale):
        """ .ctor
            Args:
                client (api.client.Client): API client
                id (int): application id
                languages (list): list of languages
        """
        self.client = client
        self.id = id
        self.languages = languages
        self.default_locale = default_locale


    @classmethod
    def from_dict(cls, client, data):
        """ Build from api response
            Args:
                client (api.client.Client): API client
                data (dict): API response
            Returns:
                Application
        """
        return Application(client, data['id'], data['languages'], data['default_locale'])


    @classmethod
    def load_default(cls, client):
        """ Load default application
            Args:
                client (api.client.Client): API client
            Returns:
                Application
        """
        return cls.from_dict(client, client.get('applications/current', {'definition': 1}))

    @classmethod
    def load_by_id(cls, client, id):
        """ Load application by id
            Args:
                client (api.client.Client): API client
                id (int): application
            Returns:
                Application
        """
        return cls.from_dict(client, client.get('applications/%d' % id, {'definition': 1}))

    def get_language_url(self, locale):
        """ Language URL for locale
            Args:
                locale (string): locale code
            Throws:
                LanguageNotSupported
            Returns:
                string: url
        """
        for language in self.languages:
            if language['locale'] == locale:
                return 'languages/%s' % locale
        raise LanguageNotSupported(locale, self)


class LanguageNotSupported(Error):
    """ Raised if somebody try to load not supported language """
    def __init__(self, locale, application):
        """ .ctor
            Args:
                locale (string): given locale code
                application (Application): application instance
        """
        self.locale = locale
        self.application = application

    def __str__(self):
        return 'Locale %s is not suppored by application %d' % (self.locale, self.application.id)
