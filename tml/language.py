from .rules.contexts import Contexts
from .rules import ContextRules
from .rules.case import Case


__author__ = 'a@toukmanov.ru'

class Language(object):
    """ Language object """
    def __init__(self, application, id, locale, native_name, right_to_left, contexts, cases):
        """ .ctor
            Args:
                application (Application): current application
                id (int): language id in API
                locale (string): language cover
                native_name (string): languge title
                right_to_left (boolean): rtl flag
                contexts (.rules.contexts.Contexts): contexts
        """
        self.applicaton = application
        self.id = id
        self.locale = locale
        self.native_name = native_name
        self.right_to_left = right_to_left
        self.contexts = contexts
        self.cases = cases

    @classmethod
    def from_dict(cls, application, data, safe = True):
        """ Build language instance from API response """
        cases, case_errors = Case.from_data(data['cases'], safe = True)
        if len(case_errors) and not safe:
            raise Exception('Language contains invalid cases', case_errors)
        return cls(application,
                   data['id'],
                   data['locale'],
                   data['native_name'],
                   data['right_to_left'],
                   Contexts.from_dict(data['contexts']),
                   cases)

    @classmethod
    def load_by_locale(cls, application, locale):
        """ Load language by locale 
            Args:
                application (Application): app instance
                locale (string): locale code (ru|en)
            Throws:
                application.LanguageIsNotSupported: language is not supported by APP
                api.client.ClientError: API error
            Returns:
                Language
        """
        # check is language supported by APP:
        url = application.get_language_url(locale)
        # load data by API:
        data = application.client.get(url, {'definition': 1})
        # create instance:
        return cls.from_dict(application, data)

    @property
    def client(self):
        return self.applicaton.client

