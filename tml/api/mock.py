# encoding: UTF-8
from urllib import urlencode
from .client import Client, HttpError
from json import loads
from os import listdir
from os.path import isdir
import re


class Hashtable(Client):
    """ Client mock: all data stored in hashtable """
    def __init__(self, data = {}, strict = False):
        """ .ctor
            Args:
                data (dict): responses key - URL, value - response
                strict (boolean): key depends params (if False - return  
        """
        self.data = data
        self.handle_nostrict = None if strict else KeyError
        # Log last request:
        self.url = None
        self.method = None
        self.params = None
        self.status = 0

    def call(self, url, method, params = {}):
        """ Emulate request
            Args:
                url (string): url part
                method (string): http method (get|post)
                params (string): request params
            Raises:
                HttpError
            Returns:
                dict
        """
        self.url = url
        self.method = method
        self.params = params
        try:
            try:
                self.status = 200
                ret = self.data[self.build_url(url, params)]
            except self.handle_nostrict:
                return self.data[url]
        except KeyError as e:
            self.status = 404
            raise HttpError(e, url, self)

    def build_url(self, url, params):
        if params is None:
            return url
        return url + '?' + urlencode(params)
    reloaded = []
    def reload(self, url, params):
        self.reloaded.append(self.build_url(url, params))


class File(Hashtable):
    """ Read data from file """
    def __init__(self, basedir, data = {}, strict = False):
        """ .ctor
            Args:
                basedir (string): basedir for files
        """
        self.basedir = basedir
        super(File, self).__init__(data, strict)

    def read(self, url, params = None, path = None, strict = False):
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
            path = '%s/%s' % (self.basedir, path)
        resp = loads(open(path).read())
        self.data[self.build_url(url, params)] = resp
        if not strict:
            self.data[url] = resp
        return self
    
    JSON_FILE = re.compile('(.*)\.json', re.I)
    JSON_PAGING = re.compile('(.*)_(\d+)\.json', re.I)

    def readdir(self, path):
        """ Read all files from directory """
        abspath = '%s/%s' % (self.basedir, path)
        for f in listdir(abspath):
            is_json = self.JSON_FILE.match(f)
            if is_json:
                is_json_paging = self.JSON_PAGING.match(f)

            if isdir(abspath + f):
                # recursive:
                self.readdir(path + f + '/')
            elif is_json:
                # url.json
                if is_json_paging:
                    # url_page.json
                    url = path + is_json_paging.group(1)
                    params = {'page': is_json_paging.group(2)}
                else:
                    url = path + is_json.group(1)
                    params = None
                self.read(url, params, path + f)
        return self

