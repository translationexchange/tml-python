import pickle
import json
from six import string_types
from ..utils import ts
from ..config import CONFIG
from .codecs import JSONCodec



__author__ = 'a@toukmanov.ru, xepa4ep'


# Stub class to ensure not passing in a `timeout` argument results in
# the default timeout
DEFAULT_TIMEOUT = object()


class BaseMemcachedAdapter(object):

    def __init__(self, server, params, library):
        if isinstance(server, string_types):
            self._servers = server.split(';')
        else:
            self._servers = server
        self.default_namespace = params['namespace']
        self.default_timeout = params['timeout']
        self._options = params.get('OPTIONS', None)
        self._lib = library
        self._client = None

    def get_backend_timeout(self, timeout=DEFAULT_TIMEOUT):
        if timeout == DEFAULT_TIMEOUT:
            timeout = self.default_timeout
        if timeout is None:
            timeout = 0
        elif int(timeout) == 0:
            # Other cache backends treat 0 as set-and-expire. To achieve this
            # in memcache backends, a negative timeout must be passed.
            timeout = -1
        if timeout > 2592000: # 60*60*24*30, 30 days
            # See http://code.google.com/p/memcached/wiki/FAQ
            # "You can set expire times up to 30 days in the future. After that
            # memcached interprets it as a date, and will expire the item after
            # said date. This is a simple (but obscure) mechanic."
            #
            # This means that we have to switch to absolute timestamps.
            timeout += int(ts())
        return int(timeout)


    @property
    def _cache(self):
        raise NotImplementedError('not impl')

    def _pickle(self, data):
        # might be overriden in differnet memcache implementations
        return data

    def _unpickle(self, payload):
        return payload

    @property
    def cache_name(self):
        return 'memcache'

    def read_only(self):
        return False

    def store(self, key, data, opts=None):
        self.debug('Cache store: %s', key)
        opts = {} if opts is None else opts
        timeout = self.get_backend_timeout(opts.get('timeout', None))
        self._cache.set(self.versioned_key(key, opts), self._pickle(data), timeout)
        return data

    def fetch(self, key, opts=None):
        data = self._cache.get(self.versioned_key(key, opts))
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
        self._cache.delete(self.versioned_key(key, opts))
        return key

    def exist(key, opts=None):
        data = self._cache.get(self.versioned_key(key, opts))
        return not data is None


class DefaultMemcachedAdapter(BaseMemcachedAdapter):

    def __init__(self, server, params):
        import memcache
        for base_class in self.__class__.__bases__:
            base_class.__init__(self, server, params, library=memcache)
        self.debug("Cache memcached-default initialized")

    @property
    def _cache(self):
        if getattr(self, '_client', None) is None:
            self._client = self._lib.Client(self._servers)
        return self._client

    def _pickle(self, data):
        return json.dumps(data)

    def _unpickle(self, payload):
        return json.loads(payload)

class PyLibMCCacheAdapter(BaseMemcachedAdapter):
    def __init__(self, server, params):
        import pylibmc
        for base_class in self.__class__.__bases__:
            base_class.__init__(self, server, params, library=pylibmc)
        self.debug("Cache memcached-pylibmc initialized")

    @property
    def _cache(self):
        if getattr(self, '_client', None) is None:
            self._client = self._lib.Client(self._servers)
            if self._options:
                self._client.behaviors = self._options
        return self._client

    def _pickle(self, data):
        return json.dumps(data)

    def _unpickle(self, payload):
        return json.loads(payload)


def MemcachedAdapterFactory(cache_builder):
    server = CONFIG.cache.get('host', '127.0.0.1:11211')
    params = {
        'OPTIONS': CONFIG.cache.get('options', {}),
        'namespace': CONFIG.cache.get('namespace', 'tml'),
        'timeout': CONFIG.cache.get('ttl', None),
        'compress': None}
    adapter_name = CONFIG.cache.get('backend', 'memcache_memcached')
    adapter = None
    if adapter_name.endswith('pylibmc'):
        adapter = cache_builder(PyLibMCCacheAdapter, BaseMemcachedAdapter)
    else:
        adapter = cache_builder(DefaultMemcachedAdapter, BaseMemcachedAdapter)
    return adapter(server, params)

