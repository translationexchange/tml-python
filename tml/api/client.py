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
from . import AbstractClient, APIError, ClientError
from ..logger import get_logger


class Client(AbstractClient):
    """ API Client """
    API_HOST = 'https://api.translationexchange.com'
    CDN_HOST = 'https://cdn.translationexchange.com'
    API_PATH = 'v1'

    def __init__(self, token):
        """ Client .ctor
            Args:
                token (string): API access token
        """
        self.token = token

    def get(self, url, params = {}):
        """ GET request to API
            Args:
                url (string): URL
                params (dict): params
            Raises:
                APIError: API returns error
            Returns:
                dict: response
        """
        return self.call(url, 'get', params)

    def post(self, url, params):
        """ POST request to API
            Args:
                url (string): URL
                params (dict): params
            Raises:
                APIError: API returns error
            Returns:
                dict: response
        """
        return self.call(url, 'post', params)

    def call(self, url, method, params=None):
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
        resp = None
        url = '%s/%s/%s' % (self.API_HOST, self.API_PATH, url)
        params.update({'access_token': self.token})
        with self.trace_call(url, method, params):
            resp = requests.request(method, url, params=params)
        ret = resp.json()
        if 'error' in ret:
            raise APIError(ret['error'], url=resp.url, client=self)
        return ret


    @contextlib.contextmanager
    def trace_call(self, url, method, params):
        tml_logger = get_logger()
        line, log_tpl = '', '%(method)s: %(url)s/%(query)s takes %(sec)s seconds.'
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

