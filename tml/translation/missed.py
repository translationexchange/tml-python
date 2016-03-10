from __future__ import absolute_import
# encoding: UTF-8
from six import iteritems
from collections import defaultdict
from json import dumps
from ..config import CONFIG


class MissedKeys(object):
    """ Object append missed key"""
    def __init__(self, client):
        self.client = client
        self.key_folder = defaultdict(set)

    def append(self, key, source_path=None):
        """ Add key to missed
            Args:
                key (Key): translation key
                source_path (string, optional): source path under which key have to be registered
        """
        source_path = CONFIG['default_source'] if source_path is None else source_path
        self.key_folder[source_path].add(key)

    def register(self, source_path):
        self.key_folder[source_path] = set()

    def prepare(self):
        """ Dict repr of keys list """
        ret = []
        for source, keys in iteritems(self.key_folder):
            ret.append({
                'source': source,
                'keys': [key.as_dict for key in keys]})
        return ret

    def submit(self, missed_keys):
        """ Submit keys over API
            Args:
                missed keys
        """
        return self.client.post('sources/register_keys', params={'source_keys': dumps(missed_keys), 'options': '{"realtime": true}'})

    def submit_all(self):
        """ Submit all missed keys to server """
        if len(self.key_folder) == 0:
            return
        ret = self.submit(self.prepare())
        self.key_folder = defaultdict(set)
        return ret
