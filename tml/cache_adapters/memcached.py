import pickle
from six import string_types
from ..config import CONFIG

__author__ = 'a@toukmanov.ru, xepa4ep'

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

    @property
    def _cache(self):
        raise NotImplementedError('not impl')


class DefaultMemcachedAdapter(BaseMemcachedAdapter):

    def __init__(self, server, params):
        import memcache
        super(DefaultMemcachedAdapter, self).__init__(server, params, library=memcache)

    @property
    def _cache(self):
        if getattr(self, '_client', None) is None:
            self._client = self._lib.Client(self._servers, pickleProtocol=pickle.HIGHEST_PROTOCOL)
        return self._client


class PyLibMCCacheAdapter(BaseMemcachedAdapter):
    def __init__(self, server, params):
        import pylibmc
        super(PyLibMCCacheAdapter, self).__init__(server, params, library=pylibmc)

    @property
    def _cache(self):
        if getattr(self, '_client', None) is None:
            self._client = self._lib.Client(self._servers)
            if self._options:
                self._client.behaviors = self._options
        return self._client


def MemcachedAdapterFactory():
    server = CONFIG.cache['host']
    params = {
        'OPTIONS': CONFIG.cache.get('options', {}),
        'namespace': CONFIG.cache.get('namespace', 'tml'),
        'timeout': CONFIG.cache.get('ttl', None),
        'compress': None}
    adapter_name = CONFIG.cache.get('backend', 'memcache_memcached')
    if adapter_name.endswith('pylibmc'):
        return PyLibMCCacheAdapter(server, params)
    else:
        return DefaultMemcachedAdapter(server, params)


