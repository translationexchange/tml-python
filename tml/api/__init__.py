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

from ..exceptions import Error
from ..logger import LoggerMixin
from six import iteritems

class AbstractClient(object):
    """ Basic API client """

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

    def call(self, url, method, params = None, opts=None):
        """ Make request to API """
        raise NotImplementedError('call is not implemented')

    def reload(self, url, params):
        """ Drop cache stub """
        pass

    def _compact_params(self, params):
        return dict((k, v) for k, v in iteritems(params) if v)


class ClientError(Error):
    """ Abstract API error """
    def __init__(self, url, client):
        """ Abtract API Error
            Args:
                url (string): rest URL
                client (Client): client instance
        """
        super(ClientError, self).__init__()
        self.client = client
        self.url = url

    def __str__(self):
        """ String repr for error """
        return 'TML API call fault to %s' % self.url


class APIError(ClientError):
    """ Exception for error given from API response """
    def __init__(self, error, url, client):
        super(APIError, self).__init__(url, client)
        self.error = error

    MESSAGE = '%s with API error: %s'
    def __str__(self):
        return self.MESSAGE % (super(APIError, self).__str__(), self.error)

