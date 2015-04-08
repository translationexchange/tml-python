# encoding: UTF-8
from . import AbstractDictionary
from tml.api.pagination import allpages
from tml.translation import Translation


class Dictionary(AbstractDictionary):
    """ Dictionary fetch translation for each key via API """
    def fetch(self, key):
        """ Translate key
            Args:
                key (Key): tranlated key
            Returns:
                Translation
        """
        return Translation.from_data(key,
                                     allpages(key.client,
                                              'translation_keys/%s/translations' % key.key,
                                              {'locale': key.language.locale}))

