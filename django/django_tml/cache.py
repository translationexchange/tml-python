from __future__ import absolute_import
# encoding: UTF-8
from django.conf import settings
from django.core.cache import caches
from tml.api.client import Client
try:
    from urllib import urlencode
except ImportError:
    # PY3
    from urllib.parse import urlencode

class CachedClient(object):
    """ Кэширующий клиент """
    def __init__(self, client, backend):
        """
        .ctor
        :param client: API client
        :param backend: Django cache backend
        :return:
        """
        self.client = client
        self.backend = backend

    @classmethod
    def instance(cls):
        client = Client(settings.TML.get('token'))
        return cls.wrap(client)

    @classmethod
    def wrap(cls, client):
        backend_name = settings.TML.get('cache', None)
        if backend_name is None:
            return client
        return cls(client, caches[backend_name])

    def key(self, url, params):
        return '%s?%s' % (url, urlencode(params))

    def get(self, url, params = {}):
        """ GET request to API 
            Args:
                url (string): URL
                params (dict): params
            Raises:
                HttpError: something wrong with connection
                APIError: API returns error
            Returns:
                dict: response
        """
        try:
            key = self.key(url, params)
            return self.read(key)
        except NotCached as readme:
            ret = self.client.get(url, params)
            self.log(url, params)
            self.backend.set(key, ret)
            return ret

    def read(self, key):
        """
        Read data from cache
        :param key:
        :return:
        """
        ret = self.backend.get(key)
        if ret is None:
            raise NotCached(key)
        return ret

    def post(self, url, params):
        return self.client.post(url, params)

    def reload(self, url, params):
        """ Drop cache """
        self.backend.delete(self.key(url, params))

    @property
    def log_key(self):
        return 'tml_cache_log_%s.%s' % (self.client.__module__, self.client.__class__.__name__)

    def log(self, *request):
        """
        Log key usage
        :param url:
        :param params:
        :return:
        """
        log_size = settings.TML.get('log_size')
        if log_size is None:
            return # Do not log:
        print self.log_key
        log = self.backend.get(self.log_key, default = [])
        if request in log:
            # URL already in log:
            return self
        log.append(request)
        if len(log) > log_size:
            # Rotate log:
            log = log[1:]
        self.backend.set(self.log_key, log)


class NotCached(Exception):
    def __init__(self, key):
        self.key = key


class Writeonly(CachedClient):
    """ Writeonly cache (for warmup) """
    def read(self, key):
        """
        Do not read any from cache
        :param key:
        :return:
        """
        raise NotCached(key)

    @property
    def keys(self):
        print self.log_key
        return self.backend.get(self.log_key, [])

    def warmup(self, *request):
        """
        Warmup cache
        :return:
        """
        self.get(*request)

    def log(self, *request):
        # Do not log:
        return self

