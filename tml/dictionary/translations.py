# encoding: UTF-8
from . import AbstractDictionary
from ..api.pagination import allpages
from ..translation import Translation
from ..api.client import ClientError
from . import TranslationIsNotExists


class Dictionary(AbstractDictionary):
    """ Dictionary fetch translation for each key via API """
    def fetch(self, key):
        """ Translate key
            Args:
                key (Key): tranlated key
            Returns:
                Translation
        """
        try:
            data = allpages(key.client, 'translation_keys/%s/translations' % key.key, {'locale': key.language.locale})
            return Translation.from_data(key, data)
        except ClientError:
            raise TranslationIsNotExists(key, self)

