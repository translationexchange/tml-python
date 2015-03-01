# encoding: UTF-8
from ..translation import Translation
from . import Hashtable
from tml.api.pagination import allpages

class LanguageDictionary(Hashtable):
    """ Load tranlations for language """
    def __init__(self, lang, missed_keys):
        """ .ctor
            Args:
                lang (Language): language
                missed_keys (list): list for missed keys
        """
        url = 'applications/%d/translations' % lang.applicaton.id
        super(LanguageDictionary, self).__init__(allpages(lang.client,
                                                          url,
                                                          {'locale': lang.locale}),
                                                 missed_keys)

