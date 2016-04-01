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
from requests.exceptions import HTTPError
import six
from ..utils import read_gzip, pj, interval_timestamp, ts
from ..config import CONFIG
from ..logger import get_logger
from ..cache import CachedClient
from ..logger import LoggerMixin
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
        return self.translator and self.translator.is_inline() or False

    def on_miss(self, key):
        return None if self.cache.read_only() else self.cdn_call(key)

    # get cache version from CDN
    def get_cache_version(self):
        # t = interval_timestamp(CONFIG['version_check_interval'])
        self.debug("Fetching cache version from CDN with timestamp")
        data = self.cdn_call('version', params={'t': ts()}, opts={'public': True, 'uncompressed': True})
        if not data:
            self.debug('No releases have been published yet')
            return '0'
        return data['version']

    def verify_cache_version(self):
        """If version is not available in cache, then ask cdn."""
        if self.cache.version.is_defined():
            return
        if not CONFIG.cache_enabled():
            return False
        cur_version = self.cache.version.fetch()
        if cur_version == 'undefined':
            self.cache.store_version(self.get_cache_version())
        else:
            pass
        self.debug('Version: %s', self.cache.version)
        return

    # cache is enabled if: get and cache enabled and cache_key
    def should_enable_cache(self, method, opts=None):
        opts = {} if not opts else opts
        if method.lower() != 'get':
            return False
        if not opts.get('cache_key', None):
            return False
        if not CONFIG.cache_enabled():
            return False
        return True


class Client(LoggerMixin, CacheFallbackMixin, AbstractClient):
    """ API Client """
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

    def cdn_call(self, key, params=None, opts=None):
        method = 'get'
        params = {} if params is None else self._compact_params(params)
        opts = {} if opts is None else self._compact_params(opts)
        version = opts.get('cache_version', None)  # force opts
        if not version:
            if self.cache.version.is_invalid() and key != 'version':
                return None
            version = self.cache.version   # use default (from config)

        uri = self.key
        response = None
        if key == 'version':
            uri = pj(uri, 'version.json')
        elif key == 'release':   # if download release
            uri = pj(uri, version + '.tar.gz')
        else:
            suffix = ('' if opts.get('uncompressed', False) else '.gz')
            uri = pj(uri, '%s/%s.json%s' % (version, key, suffix))
        url = pj(CONFIG.cdn_host(), uri)
        try:
            with self.trace_call(url, method, params):
                response = requests.request(method, url, **self._request_config(method, params))
                return self.process_response(response, opts)
        except HTTPError as e:
            self.debug("HTTP RESPONSE ERROR for request %s", e.response.url)
            return None

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
        empty_ret = {'results': {}}
        params = {} if params is None else self._compact_params(params)
        opts = {} if opts is None else self._compact_params(opts)
        # self.debug("IS LIVE MODE ACTIVATED: %s", self.is_live_api_request())
        if self.is_live_api_request():
            try:
                return self.process_response(
                    self._api_call(url, method, params=params, opts=opts),
                    opts=opts)
            except HTTPError as e:
                self.debug("HTTP RESPONSE ERROR for request %s", e.response.url)
                return empty_ret
        else:
            data = None
            if self.should_enable_cache(method, opts):
                self.verify_cache_version()
                if self.cache.version.is_valid():
                    data = self.cache.fetch(
                        opts['cache_key'], opts={'miss_callback': self.on_miss})
            return data or empty_ret

    def _api_call(self, uri, method, params=None, opts=None):
        response = None
        url = '%s/%s/%s' % (CONFIG.api_host(), self.API_PATH, uri)
        params['app_id'] = self.key
        if not opts.get('public', None):
            params['access_token'] = self.access_token

        with self.trace_call(url, method, params):
            return requests.request(method, url, **self._request_config(method, params))

    def _request_config(self, method, params):
        headers = {'user-agent': 'tml-python v0.0.1',
                   'accept': 'application/json',
                   'accept-encoding': 'gzip, deflate'}
        config = {'timeout': 30, 'headers': headers}
        params = {k: str(v).lower() if type(v) is bool else v
                  for k, v in six.iteritems(params)}
        if method == 'post':
            headers['content-type'] = 'application/x-www-form-urlencoded'
            config['data'] = params
        else:
            config['params'] = params
        return config

    def process_response(self, response, opts):
        if response is None:  # response is empty
            return
        data = None
        if not isinstance(response, Response) and not (opts.get('response_class', None) and isinstance(response, opts['response_class'])):
            return response
        if 500 <= response.status_code < 600:   # server error occured
            raise APIError(response.text, url=response.url, client=self)
        response.raise_for_status()
        compressed = response.request.method.lower() == 'get'   # if get then compressed result
        if opts.get('raw', False):   # no need to deserialize and uncompress
            return response.content
        if compressed and not opts.get('uncompressed', False):   # need uncompress
            compressed_data = response.content
            if not compressed_data:  # empty response
                return None

            if response.url.startswith(CONFIG.api_host()):
                data = compressed_data   # requests automatically decompresses
            else:
                data = read_gzip(compressed_data)

            self.debug("Compressed: %s, uncompressed: %s", len(compressed_data), len(data))
        else:
            data = response.text
        try:
            data = json.loads(data)
        except Exception as e:
            data = None
        if opts.get('wrapper', None):   # either class or fn wrappers/modifiers
            data = opts['wrapper'](data)
        if isinstance(data, (list, dict)):
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
            six.reraise(*exc_info)
        else:
            t1 = time.time()
            tml_logger.debug(log_tpl % dict(method=method.upper(), url=url, query=self.to_query(params), sec=int(t1 - t0)))

    def to_query(self, params):
        querystr = ['%s=%s' % (k, v) for k, v in six.iteritems(params)]
        return '&'.join(querystr)


if CONFIG.verbose:
    # Enabling debugging at http.client level (requests->urllib3->http.client)
    # you will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # the only thing missing will be the response.body which is not logged.
    import logging
    from six import http_client
    try: # for Python 3
        from http.client import HTTPConnection
    except ImportError:
        from httplib import HTTPConnection
    HTTPConnection.debuglevel = 1

    logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
