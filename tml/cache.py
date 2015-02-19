# -*- coding: utf-8 -*-
""" Cached API client for api.translationexchange.com """
from urllib import urlencode

class CachedClient(object):
    """ Cached client """
    def __init__(self, client, cache):
        """ Http API Client
            Args:
                client (tml.api.Client): HttpClient
                cache (tpl.cache.Adapter): cache
        """
        self.client = client
        self.cache = cache

    def get_from_cache(self, url, params):
        """ Get data from cache """
        return self.cache.get(url)

    def set_cache(self, url, value):
        """ Put data to cache 
            Args:
                url (string): cache key
                value (string): cache value
            Return
        """
        self.cache.set(url, value)
        return value

    def build_key(self, url, params):
        return '%s?%s' % (url, urlencode(params))

    def get(self, url, params):
        """ Call API method """
        try:
            # Check cache:
            key = self.build_key(url, params)
            ret = self.get_from_cache(key)
        except KeyError:
            # Key in cache does not exists:
            ret = self.client.get(url, params)
            return self.set_cache(key, value)


class Adapter(object):
    """ Abstract cache adapter """
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data[key]

    def set(self, key, value):
        self.data[key] = value

class Readonly(object):
    """ Readonly wrapper for cache """
    def __init__(self, adapter):
        self.adapter = adapter

    def get(self, key):
        return self.adapter.get(key)

    def set(self, key, value):
        pass

class Writeonly(object):
    """ Writeonly wrapper for cache object (used for warmup) """
    def __init__(self, adapter):
        self.adapter = adapter

    def get(self, key):
        raise KeyError()

    def set(self, key, value):
        self.adapter.set(key, value)

