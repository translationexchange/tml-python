import pickle
import json
from six import string_types
from ..utils import ts
from ..config import CONFIG
from .codecs import JSONCodec

__author__ = 'a@toukmanov.ru, xepa4ep'

DEFAULT_TIMEOUT = object()


class BaseRedisAdapter(object):

    def __init__(self, server, params, library):
        if isinstance(server, string_types):
            self._servers = server.split(';')
        else:
            self._servers = server
        self.default_namespace = params['namespace']
        self.default_timeout = params['timeout']
        self._options = params.get('OPTIONS', {})
        self._lib = library
        self._client = None

    def get_backend_timeout(self, timeout=DEFAULT_TIMEOUT):
        if timeout == DEFAULT_TIMEOUT:
            timeout = self.default_timeout
        if timeout is None:
            timeout = 0
        elif int(timeout) == 0:
            timeout = -1
        if timeout > 2592000:
            timeout += int(ts())
        return int(timeout)


    @property
    def _cache(self):
        raise NotImplementedError('not impl')

    def _pickle(self, data):
        return data

    def _unpickle(self, payload):
        return payload

    @property
    def cache_name(self):
        return 'redis'

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

class DefaultRedisAdapter(BaseRedisAdapter):

    def __init__(self, server, params):
        import redis
        for base_class in self.__class__.__bases__:
            base_class.__init__(self, server, params, library=redis)
        self.debug("Cache redis-default initialized")

    @property
    def _cache(self):
        server, port = self._servers[0].split(':')
        if getattr(self, '_client', None) is None:
            if self._options.get('pool', False):
                self._client = self._lib.ConnectionPool(max_connections=self._options.get('max_connections', 10), host=server, port=port)
            else:
                self._client = self._lib.Redis(server, port)
        return self._client

    def _pickle(self, data):
        return json.dumps(data)

    def _unpickle(self, payload):
        return json.loads(payload.decode())

def RedisAdapterFactory(cache_builder):
    server = CONFIG.cache.get('host', '127.0.0.1:6379')
    params = {
        'OPTIONS': CONFIG.cache.get('options', {}),
        'namespace': CONFIG.cache.get('namespace', 'tml'),
        'timeout': CONFIG.cache.get('ttl', None),
        'compress': None}
    #adapter_name = CONFIG.cache.get('backend', 'redis_default')
    adapter = None
    adapter = cache_builder(DefaultRedisAdapter, BaseRedisAdapter)

    return adapter(server, params)
