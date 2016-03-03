# encoding: UTF-8
from ..config import CONFIG
from ..strings import to_string
import json
import os

__author__ = 'a@toukmanov.ru, xepa4ep'

class FileAdapter(object):

    cache = {}

    def get_cache_path(self):
        return os.path.join(CONFIG['cache']['path'], CONFIG['cache']['version'])

    def file_path(self, key):
        return os.path.join(self.get_cache_path(), '%s.json' % key)

    @property
    def cache_name(self):
        return 'file'

    def fetch(self, key, opts=None):
        if key in self.cache:
            self.debug("memory hit: %s", key)
            return self.cache[key]
        path = self.file_path(key)
        if os.path.exists(path):
            self.debug('cache hit: %s', key)
            with open(path) as fp:
                self.cache[key] = json.loads(to_string(fp.read()))
            return self.cache[key]
        self.debug('cache miss: %s', key)
        if opts and opts.get('miss_callback', None):
            if callable(opts['miss_callback']):
                return opts['miss_callback'](key)
        return

    def read_only(self):
        return True

    @classmethod
    def generate(cls, *args, **kwargs):
        pass
