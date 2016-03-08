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
import json
from os import listdir
from os.path import isdir
import re
from codecs import open
from six.moves.urllib.parse import urlencode
from six import iteritems
from . import AbstractClient, APIError

__author__ = 'xepa4ep, a@toukmanov.ru'


def clean_url(url):
    _url = '/'.join([
        part.rstrip('/') for part in url.split('definition')])
    if _url.endswith('/'):
        return _url[:-1]
    return _url

def debug(data, contains=''):
    return list(k for k, v in iteritems(data) if contains in k)


REWRITE_RULES = (
    ('projects/current/definition?locale=ru', 'projects/current'),
    ('projects/current/definition', 'projects/current'),
    (r'^projects\/(\w+)\/definition', 'projects/%(0)s'),
    (r'^projects\/(\w+)\/definition.*[\?\&]locale=(\w+).*$', 'projects/%(0)s?locale=%(1)s'),
    (r'^languages\/(\w+)\/definition$', 'languages/%(0)s'),
    (r'^sources\/(\w+)\/translations.*[\?\&]locale=(\w+).*$', 'sources/%(0)s/translations?locale=%(1)s'),
    (r'^translation_keys\/(\w+)\/translations\?locale=(\w+)&page=(\d+).*$', 'translation_keys/%(0)s/translations?locale=%(1)s&page=%(2)s')
)

def rewrite_path(url):
    for pattern, replacer in REWRITE_RULES:
        if pattern == url:  # if equal
            url = replacer
        else: # if match by regex
            match_obj = re.compile(pattern).match(url)
            if not match_obj:
                continue
            ctx = dict([(str(idx), v) for idx, v
                        in enumerate(match_obj.groups())])
            url = replacer % ctx
    return url.split('?')[0], url, len(url.split('?')) == 2


class Hashtable(AbstractClient):
    """ Client mock: all data stored in hashtable """
    last_url = ''
    last_params = {}
    def __init__(self, data = {}, strict = False):
        """ .ctor
            Args:
                data (dict): responses key - URL, value - response
                strict (boolean): key depends params (if False - return
        """
        super(Hashtable, self).__init__()
        self.data = data
        self.handle_nostrict = None if strict else KeyError
        # Log last request:
        self.url = None
        self.method = None
        self.params = None
        self.status = 0

    def call(self, url, method, params = None, opts=None):
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
        params = {} if params is None else self._compact_params(params)
        opts = {} if opts is None else self._compact_params(opts)
        self.__class__.last_url = url
        self.__class__.last_params = params
        self.url = url
        self.method = method
        self.params = params = {} if params is None else self._compact_params(params)
        try:
            try:
                self.status = 200
                url, url_with_params, has_params = self.rewrite_path(self.build_url(url, params))
                self.url = url
                return self.data[url_with_params]
            except self.handle_nostrict as e:
                # print self.rewrite_path(self.build_url(url, params)), debug(self.data, 'projects/2'), url
                return self.data[url]
        except KeyError as key_not_exists:
            self.status = 404
            raise APIError(key_not_exists, url, self)

    @classmethod
    def build_url(cls, url, params):
        """ Build full URL
            Args:
                url (string): url
                params (dict): get params
            Returns:
                string: url with joined get params
        """

        if params is None:
            return url
        not_important_params = ('all', )
        for param in not_important_params:
            params.pop(param, None)
        sorted_params = sorted(params.items(), key=lambda cur: cur[0])
        return url + ('' if not params else '?' + urlencode(sorted_params))

    reloaded = []

    def reload(self, url, params):
        self.reloaded.append(Hashtable.build_url(url, params))

    @classmethod
    def rewrite_path(cls, url):
        """ Build path from URL
            Args:
                url (string): API url
            Returns:
                string: path in snapshot matches API URL
        """
        return rewrite_path(url)


class File(Hashtable):
    """ Read data from file """
    def __init__(self, basedir, key=None, access_token=None, data = {}, strict = False):
        """ .ctor
            Args:
                basedir (string): basedir for files
        """
        self.basedir = basedir
        self.key = key
        self.access_token = access_token
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
        url = clean_url(url)
        path = path if path else '%s.json' % url
        if path[0] != '/':
            # relative path:
            path = '%s/%s' % (self.basedir, path)
        with open(path, 'rb') as fp:
            resp = json.loads(fp.read().decode('utf-8'))
        self.data[self.build_url(url, params)] = resp
        if not strict:
            self.data[url] = resp
        return self

    JSON_FILE = re.compile('(.*)\.json', re.I)
    JSON_PAGING = re.compile('(.*)_(\d+)\.json', re.I)

    def readdir(self, path):
        """ Read all files from directory """
        abspath = '%s/%s' % (self.basedir, path)

        for dir_or_fname in listdir(abspath):
            is_json = self.JSON_FILE.match(dir_or_fname)
            if is_json:
                is_json_paging = self.JSON_PAGING.match(dir_or_fname)

            if isdir(abspath + dir_or_fname):
                # recursive:
                self.readdir(path + dir_or_fname + '/')
            elif is_json:
                # url.json
                if is_json_paging:
                    # url_page.json
                    url = path + is_json_paging.group(1)
                    params = {'page': is_json_paging.group(2)}
                else:
                    url = path + is_json.group(1)
                    params = None
                self.read(url, params, path + dir_or_fname)
        return self

