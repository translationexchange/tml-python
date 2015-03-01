# encoding: UTF-8
from tml.translation import Translation

class AbstactDictionary(object):
    """ Dictionary """
    def __init__(self, missed_keys):
        """ Dictionary .ctor
            Args:
                missed_keys (list): list of missed keys or object with append method
        """
        self.missend_keys = missed_keys

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
            self.missend_keys.append(key)
            # Returns empty translation:
            return Translation(key, [])

    def fetch(self, key):
        raise NotImplemented()

