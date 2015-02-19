# encoding: UTF-8
# --
# Copyright (c) 2015, Translation Exchange, Inc.
#
#  _______                  _       _   _             ______          _
# |__   __|                | |     | | (_)           |  ____|        | |
#    | |_ __ __ _ _ __  ___| | __ _| |_ _  ___  _ __ | |__  __  _____| |__   __ _ _ __   __ _  ___
#    | | '__/ _` | '_ \/ __| |/ _` | __| |/ _ \| '_ \|  __| \ \/ / __| '_ \ / _` | '_ \ / _` |/ _ \
#    | | | | (_| | | | \__ \ | (_| | |_| | (_) | | | | |____ >  < (__| | | | (_| | | | | (_| |  __/
#    |_|_|  \__,_|_| |_|___/_|\__,_|\__|_|\___/|_| |_|______/_/\_\___|_| |_|\__,_|_| |_|\__, |\___|
#                                                                                        __/ |
#                                                                                       |___/
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
#++

__author__ = 'randell'

import requests, json
from ..exceptions import Error


class Client(object):
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
        """ Call API method """
        try:
            url = '%s/%s/%s' % (self.API_HOST, self.API_PATH, url)
            params.update({'token': self.token})
            resp = requests.get(url, params)
            resp.raise_for_status() # check http status
            ret = resp.json()
            if 'error' in ret:
                raise APIError(ret['error'], url = url, client = self)
            return ret
        except Exception as e:
            raise HttpError(e, url = url, client = self)


class ClientError(Error):
    """ Abstract API error """
    def __init__(self, url, client):
        """ Abtract API Error
            Args:
                url (string): rest URL
                client (Client): client instance
        """
        self.client = client
        self.url = url

    def __str__(self):
        """ String repr for error """
        return 'TML API call fault to %s' % self.url


class HttpError(ClientError):
    """ Something wrong whith HTTP """
    def __init__(self, error, url, client):
        super(HttpError, self).__init__(url, client)
        self.error = error

    def __str__(self):
        return '%s with %s: %s' % (super(HttpError, self).__str__(), self.error.__class__.__name__, self.error)


class APIError(ClientError):
    def __init__(self, error, url, client):
        super(HttpError, self).__init__(url, client)
        self.error = error

    def __str__(self):
        return '%s with API error: %s' % (super(HttpError, self).__str__(), self.error)

