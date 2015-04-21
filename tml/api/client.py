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
__author__ = 'a@toukmanov.ru'


import requests
from . import AbstractClient, APIError, ClientError

class Client(AbstractClient):
    """ API Client """
    API_HOST = 'https://api.translationexchange.com'
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
                HttpError: something wrong with connection
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
                HttpError: something wrong with connection
                APIError: API returns error
            Returns:
                dict: response
        """
        return self.call(url, 'post', params)

    def call(self, url, method, params = {}):
        """ Make request to API 
            Args:
                url (string): URL
                method (string): HTTP method (get|post|put|delete)
                params (dict): params
            Raises:
                HttpError: something wrong with connection
                APIError: API returns error
            Returns:
                dict: response
        """
        resp = None
        try:
            url = '%s/%s/%s' % (self.API_HOST, self.API_PATH, url)
            params.update({'access_token': self.token})
            resp = requests.request(method, url, params = params)
            ret = resp.json()
        except Exception as http_error:
            raise HttpError(http_error,
                            url = resp.url if resp is not None else url,
                            client = self)
        if 'error' in ret:
            raise APIError(ret['error'], url = resp.url, client = self)
        return ret


class HttpError(ClientError):
    """ Something wrong whith HTTP """
    def __init__(self, error, url, client):
        super(HttpError, self).__init__(url, client)
        self.error = error

    MESSAGE = '%s with %s: %s'
    def __str__(self):
        return self.MESSAGE % (super(HttpError, self).__str__(),
                               self.error.__class__.__name__,
                               self.error)

