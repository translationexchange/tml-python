# encoding: UTF-8
from tml.api.client import HttpError
from json import loads
from os.path import dirname
from urllib import urlencode

FIXTURES_PATH = '%s/fixtures' % dirname(dirname(__file__))

URLS = [('applications/current', {'definition': 1}),
        ('applications/2', {'definition': 1}),
        ('languages/ru', {'definition': 1}),
        ('applications/1/translations', {'locale':'ru'}),
        ('sources/register_keys', None),
        ('tranlation_keys/translation', {'locale':'ru'})]

class Client(object):
    def __init__(self, data = {}):
        self.data = data

    def build_url(self, url, params):
        return '%s?%s' % (url, urlencode(params))

    def request(self, method, url, params):
        self.method = method
        self.url = url
        self.params = params
        try:
            url = self.build_url(url, params) if method == 'get' else url 
            return self.data[url]
        except KeyError as e:
            raise HttpError(e, url, self)

    def get(self, url, params = None):
        return self.request('get', url, params)

    def post(self, url, params = None):
        """ POST data """
        return self.request('post', url, params)

    def read(self, url, params = {}, path = None):
        """ Read response
            Args:
                url (string): for URL
                params (dict): with params
                path (string): from file (url.json - by default)
            Returns:
                Client
        """
        path = path if path else '%s.json' % url
        if path[0] != '/':
            # relative path:
            path = '%s/%s' % (FIXTURES_PATH, path)
        url = self.build_url(url, params) if params is not None else url
        self.data[url] = loads(open(path).read())
        return self

    @classmethod
    def read_all(cls):
        ret = cls()
        for url, params in URLS:
            ret.read(url, params)
        return ret