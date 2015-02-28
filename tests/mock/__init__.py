# encoding: UTF-8
from tml.api.client import HttpError
from json import loads
from os.path import dirname
from urllib import urlencode

FIXTURES_PATH = '%s/fixtures' % dirname(dirname(__file__))

class Client(object):
    def __init__(self, data = {}):
        self.data = data

    def build_url(self, url, params):
        return '%s?%s' % (url, urlencode(params))

    def get(self, url, params = None):
        try:
            return self.data[self.build_url(url, params)]
        except KeyError as e:
            raise HttpError(e, url, self)

    def read(self, url, params, path = None):
        path = path if path else '%s.json' % url
        if path[0] != '/':
            # relative path:
            path = '%s/%s' % (FIXTURES_PATH, path)
        self.data[self.build_url(url, params)] = loads(open(path).read())
