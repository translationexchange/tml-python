# encoding: UTF-8
from tml.api.client import HttpError
from json import loads
from os.path import dirname

FIXTURES_PATH = '%s/fixtures' % dirname(dirname(__file__))

class Client(object):
    def __init__(self, data = {}):
        self.data = data

    def get(self, url, params = None):
        try:
            return self.data[url]
        except KeyError as e:
            raise HttpError(e, url, self)

    def read(self, url, path = None):
        path = path if path else '%s.json' % url
        if path[0] != '/':
            # relative path:
            path = '%s/%s' % (FIXTURES_PATH, path)
        self.data[url] = loads(open(path).read())

