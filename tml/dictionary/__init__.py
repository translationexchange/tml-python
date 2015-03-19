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


class AbstactDictionary(object):
    """ Dictionary """
    def __init__(self, missed_keys, fallback = None):
        """ Dictionary .ctor
            Args:
                missed_keys (list): list of missed keys or object with append method
        """
        self.missed_keys = missed_keys
        self.fallback = fallback if fallback else return_label_fallback

    def translate(self, key):
        """ Get key tranlation
            Args:
                key (Key): tranlated key
            Returns:
                Translation
        """
        try:
            return self.fetch(key)
        except Error as e:
            self.missed_keys.append(key)
            return self.fallback(key)

    def fetch(self, key):
        raise NotImplemented()


class Hashtable(AbstactDictionary):
    """ Dictionary with translation store in hash """
    def __init__(self, tranlations = None, missed_keys = []):
        """ .ctor
            Args:
                tranlations (dict): key- tranlation code, value - tranlation options
        """
        self.tranlations = tranlations
        super(Hashtable, self).__init__(missed_keys)

    """ Hash dictionary """
    def fetch(self, key):
        """ Tranlate key 
            Args:
                key (Key): translated key
            Returns:
                Tranlation
        """
        return Translation.from_data(key, self.tranlations[key.key])

