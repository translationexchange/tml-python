# -*- coding: utf-8 -*-
""" API client for api.translationexchange.com """
import requests
from tml.exceptions import Error

class Client(object):
    """ TransationExchange API Client """
    def __init__(self, token, host = 'api.translationexchange.com', version = 1, timeout = 10):
        """ Http API Client
            Args:
                host (string): API host
                version (int): version
                timeout (int): connection timeout (seconds)
        """
        self.token = token
        self.host = host
        self.version = 1

    def get(self, url, params = {}):
        """ Call API method """
        try:
            url = 'https://%s/v%d/%s' % (self.host, self.version, url)
            params.update({'token': self.token})
            resp = requests.get(url, params)
            resp.raise_for_status() # check http status
            ret = resp.json()
            if 'error' in ret:
                raise APIError(ret['error'], url = url, client = self)
            return ret
        except Exception as e:
            raise HttpError(e, url = url, client = self)


def allpages(client, url, params = {}):
    """ Load all pages """
    res = client.get(url, params)
    ret = res['results']
    while (res['pagination']['current_page'] < res['pagination']['total_pages']):
        params['page'] = int(res['pagination']['current_page']) + 1
        res = client.get(url, params)
        ret.append(res['results'])
    return ret



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

class HttpError(Error):
    """ Something wrong whith HTTP """
    def __init__(self, error, url, client):
        super(HttpError, self).__init__(url, client)
        self.error = error

    def __str__(self):
        return '%s with %s: %s' % (super(HttpError, self).__str__(), e.__class__.__name__, e)

class APIError(Error):
    def __init__(self, error, url, client):
        super(HttpError, self).__init__(url, client)
        self.error = error

    def __str__(self):
        return '%s with API error: %s' % (super(HttpError, self).__str__(), e.__class__.__name__, e)
