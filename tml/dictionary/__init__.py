# encoding: UTF-8
from ..translation import Translation
from ..exceptions import Error


def return_label_fallback(key):
    """ Fallaback tranlation
        Args:
            key (Key): translated key
        Returns:
            Translation
    """
    return Translation(key, [])


class AbstractDictionary(object):
    """ Dictionary """
    def __init__(self, fallback = None):
        """ Dictionary .ctor
            Args:
                fallback (function): function which generate tranlation if current is not found
        """
        self._fallback = fallback if fallback else return_label_fallback

    def translate(self, key):
        """ Get key tranlation
            Args:
                key (Key): tranlated key
            Returns:
                Translation
        """
        try:
            return self.fetch(key)
        except Exception as e:
            return self.fallback(key)

    def fetch(self, key):
        raise NotImplemented()

    def fallback(self, key):
        """ Key is not found """
        return self._fallback(key)

    @property
    def fallback_function(self):
        return self._fallback


class Hashtable(AbstractDictionary):
    """ Dictionary with translation store in hash """
    def __init__(self, translations = None, fallback = None):
        """ .ctor
            Args:
                tranlations (dict): key- tranlation code, value - tranlation options
        """
        self.translations = translations
        super(Hashtable, self).__init__(fallback)

    """ Hash dictionary """
    def fetch(self, key):
        """ Tranlate key 
            Args:
                key (Key): translated key
            Returns:
                Tranlation
        """
        return Translation.from_data(key, self.translations[key.key])

