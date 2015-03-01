# encoding: UTF-8
from json import dumps

class MissedKey(object):
    """ Object append missed key"""
    def __init__(self, client):
        self.client = client

    def append(self, key):
        """ Add key to missed
            Args:
                key (Key): translation key
        """
        missed_keys = [{'keys':[key.as_dict]}]
        return self.submit(missed_keys)

    def submit(self, missed_keys):
        """ Submit keys over API
            Args:
                missed keys
        """
        return self.client.post('sources/register_keys',{'source_keys': dumps(missed_keys)})


class MissedKeysLazy(MissedKey):
    """ Submit all missed keys once """
    keys = []
    def append(self, key):
        """ Add key to missed
            Args:
                key (Key): translation key
        """
        self.keys.append(key)

    def submit_all(self):
        if len(self.keys) == 0:
            return
        missed_keys = [{'keys':[key.as_dict for key in self.keys]}]
        ret = self.submit(missed_keys)
        self.keys = []
        return ret

