import json
from tml.config import CONFIG


class DjangoCacheAdapter(object):

    def __init__(self, backend, params):
        self.backend = backend
        self.install(params.copy())

    def install(self, params):
        from django.core.cache import _create_cache
        params.update({
            'KEY_PREFIX': '',
            'VERSION': '',
            'KEY_FUNCTION': self.make_key})
        self._cache = _create_cache(self.backend, **params)

    @property
    def cache_name(self):
        return 'django_' + self.backend

    def read_only(self):
        return False

    def make_key(self, key, *args, **kwargs):
        return self.versioned_key(key)

    def _pickle(self, data):
        return json.dumps(data)

    def _unpickle(self, payload):
        return json.loads(payload)

    def store(self, key, data, opts=None):
        self.debug('Cache store: %s', key)
        opts = {} if opts is None else opts
        timeout = opts.get('timeout', None)
        self._cache.set(key, self._pickle(data), timeout)
        return data

    def fetch(self, key, opts=None):
        data = self._cache.get(key)
        if data:
            self.debug('Cache hit: %s', key)
            data = self._unpickle(data)
        else:
            if opts and opts.get('miss_callback', None):
                if callable(opts['miss_callback']):
                    data = opts['miss_callback'](key)
            self.store(key, data)
            self.debug('Cache miss: %s', key)
        return data

    def delete(self, key, opts=None):
        self.debug('Cache delete: %s', key)
        self._cache.delete(key)
        return key

    def exist(key, opts=None):
        data = self._cache.get(key)
        return not data is None


def DjangoCacheFactory(cache_builder):
    server = CONFIG.cache.get('host', '127.0.0.1:11211')
    params = {
        'LOCATION': server,
        'OPTIONS': CONFIG.cache.get('options', {}),
        'TIMEOUT': CONFIG.cache.get('ttl', None)}
    backend_name = CONFIG.cache.get('backend', 'django.core.cache.backends.memcached.MemcachedCache')
    adapter = cache_builder(DjangoCacheAdapter)
    return adapter(backend_name, params)
