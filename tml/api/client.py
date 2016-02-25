# encoding: UTF-8
"""
# Copyright (c) 2015, Translation Exchange, Inc.
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import absolute_import
__author__ = 'a@toukmanov.ru, xepa4ep'

import sys
import time
import requests
import contextlib
import json
from requests import Response
from ..utils import read_gzip, pj
from ..config import CONFIG
from ..logger import get_logger
from ..cache import CachedClient
from ..session_vars import get_current_translator
from . import AbstractClient, APIError, ClientError


class CacheFallbackMixin(object):

    @property
    def cache(self):
        return CachedClient.instance()

    @property
    def translator(self):
        return get_current_translator()

    def is_live_api_request(self):
        if not self.access_token: # if no access token, never use live mode
            return False
        return self.translator and self.translator.is_inline()

    def on_miss(self, key):
        return None if self.cache.read_only() else self.cdn_call(key)

    # get cache version from CDN
    def get_cache_version(self):
        t = interval_timestamp(CONFIG['version_check_interval'])
        self.debug("Fetching cache version from CDN with timestamp: %s", t)
        data = self.cdn_call('version', params={'t': t}, opts={'public': True, 'uncompressed': True})
        if not data:
            self.debug('No releases have been published yet')
            return '0'
        return data['version']

    def verify_cache_version(self):
        """If version is not available in cache, then ask cdn."""
        if not CONFIG.cache_enabled():
            return False
        cur_version = self.cache.version.fetch()
        if cur_version == 'undefined':
            self.cache.store_version(self.get_cache_version())
        else:
            self.cache.version.set(cur_version)
        self.debug('Version: %s', self.cache.version)
        return

    # cache is enabled if: get and cache enabled and cache_key
    def should_enable_cache(self, method, opts=None):
        return method != 'get' and CONFIG.cache_enabled() and opts['cache_key'] is not None


class Client(CacheFallbackMixin, AbstractClient):
    """ API Client """
    API_HOST = 'https://api.translationexchange.com'
    CDN_HOST = 'https://cdn.translationexchange.com'
    API_PATH = 'v1'

    def __init__(self, key, access_token=None):
        """ Client .ctor
            Args:
                token (string): API access token
        """
        self.key = key
        self.access_token = access_token

    def get(self, url, **kwargs):
        """ GET request to API
            Args:
                url (string): URL
                params (dict): params
            Raises:
                APIError: API returns error
            Returns:
                dict: response
        """
        return self.call(url, 'get', **kwargs)

    def post(self, url, **kwargs):
        """ POST request to API
            Args:
                url (string): URL
                params (dict): params
            Raises:
                APIError: API returns error
            Returns:
                dict: response
        """
        return self.call(url, 'post', **kwargs)

    def cdn_call(self, key, method, params=None, opts=None):
        params = {} if params is None else self._compact_params(params)
        opts = {} if opts is None else self._compact_params(opts)
        if self.cache.version.is_invalid() and key != 'version':
            return None
        uri = self.key
        response = None
        if key == 'version':
            uri += '%s.json' % key
        else:
            uri += '%s/%s.json.gz' % (self.cache.version, key)
        with self.trace_call(pj(self.CDN_HOST, uri), method, params):
            options, headers = self.request_config()
            response = requests.request(method, url, params=params, headers=headers, **options)
            return self.process_response(response, opts)

    def call(self, url, method, params=None, opts=None):
        """ Make request to API
            Args:
                url (string): URL
                method (string): HTTP method (get|post|put|delete)
                params (dict): params
            Raises:
                APIError: API returns error
            Returns:
                dict: response
        """
        params = {} if params is None else self._compact_params(params)
        opts = {} if opts is None else self._compact_params(opts)
        if self.is_live_api_request():
            return self.process_response(
                self._api_call(url, method, params=params, opts=opts),
                opts=opts)
        else:
            data = None
            if self.should_enable_cache(method, opts):
                self.verify_cache_version()
                if self.cache.is_valid():
                    data = self.cache.fetch(
                        opts['cache_key'], opts={'miss_callback': self.on_miss})
            return data or {'results': {}}

    def _api_call(self, uri, method, params=None, opts=None):
        response = None
        url = '%s/%s/%s' % (self.API_HOST, self.API_PATH, uri)
        if not opts.get('public', None) and not 'access_token' in params:
            params['access_token'] = self.access_token
        if method == 'post':
            params['app_id'] = self.key

        with self.trace_call(url, method, params):
            options, headers = self.request_config()
            return requests.request(method, url, params=params, headers=headers, **options)

  #   def prepare_request(request, path, params)
  #   request.options.timeout = 5
  #   request.options.open_timeout = 2
  #   request.headers['User-Agent']       = "tml-ruby v#{Tml::VERSION} (Faraday v#{Faraday::VERSION})"
  #   request.headers['Accept']           = 'application/json'
  #   request.headers['Accept-Encoding']  = 'gzip, deflate'
  #   request.url(path, params)
  # end

    def request_config(self):
        options = {'timeout': 5}
        headers = {'User-Agent': 'tml-python v0.0.1',
                   'Accept': 'application/json',
                   'Accept-Encoding': 'gzip, deflate'}
        return (options, headers)

    def process_response(self, response, opts):
        if response is None:  # response is empty
            return
        data = None
        if not isinstance(response, Response) and not (opts.get('response_class', None) and isinstance(response, opts['response_class'])):
            return response
        if 500 <= response.status_code < 600:   # server error occured
            raise APIError(response.text, url=response.url, client=self)
        compressed = response.request.method.lower() == 'get'   # if get then compressed result
        if compressed and not opts.get('uncompressed', False):   # need uncompress
            compressed_data = response.content
            if not compressed_data:  # empty response
                return None

            read_gzip = lambda x: x   # temp
            data = read_gzip(compressed_data)
            self.debug("Compressed: %s, uncompressed: %s", len(compressed_data), len(data))
        else:
            data = response.text
        if opts.get('raw', False):   # no need to deserialize
            return data
        try:
            data = json.loads(data)
        except Exception as e:
            data = None
        if opts.get('wrapper', None):   # either class or fn wrappers/modifiers
            data = opts['wrapper'](data)
        if 'error' in data:   # if service error
            raise APIError(data['error'], url=response.url, client=self)
        return data

    @contextlib.contextmanager
    def trace_call(self, url, method, params):
        tml_logger = get_logger()
        line, log_tpl = '', '%(method)s: %(url)s?%(query)s takes %(sec)s seconds.'
        method = method.upper()
        query = params and self.to_query(params) or ''
        t0 = time.time()
        try:
            yield
        except Exception as e:
            tml_logger.exception(e)
            exc_info = sys.exc_info()
            raise exc_info[0], exc_info[1], exc_info[2]
        else:
            t1 = time.time()
            tml_logger.debug(log_tpl % dict(method=method.upper(), url=url, query=self.to_query(params), sec=int(t1 - t0)))

    def to_query(self, params):
        querystr = ['%s=%s' % (k, v) for k, v in params.iteritems()]
        return '&'.join(querystr)

