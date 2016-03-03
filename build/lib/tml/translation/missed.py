from __future__ import absolute_import
# encoding: UTF-8
from json import dumps
from urllib import quote

class MissedKeys(object):
    """ Object append missed key"""
    def __init__(self, client):
        self.client = client
        self.keys = set([])

    def submit(self, missed_keys):
        """ Submit keys over API
            Args:
                missed keys
        """
        return self.client.post('sources/register_keys', params={'source_keys': dumps(missed_keys), 'options': '{"realtime": true}'})

    def append(self, key):
        """ Add key to missed
            Args:
                key (Key): translation key
        """
        self.keys.add(key)

    def as_dict(self):
        """ Dict repr of keys list """
        return {'keys': [key.as_dict for key in self.keys]}

    def submit_all(self):
        """ Submit all missed keys to server """
        if len(self.keys) == 0:
            return
        missed_keys = [self.as_dict()]
        ret = self.submit(missed_keys)
        self.keys = []
        return ret


class Composite(object):
    """ Composite missed key """
    def __init__(self, *args):
        self.missed = args

    def append(self, key):
        for m in self.missed:
            m.append(key)

    def submit_all(self):
        for m in self.missed:
            m.submit_all()
