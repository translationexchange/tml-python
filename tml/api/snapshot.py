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
__author__ = 'a@toukmanov.ru'

from . import AbstractClient, APIError
from tarfile import TarFile
from json import loads
from os.path import isdir, exists
from ..exceptions import Error


LANGUAGE_PREFIX = 'languages/'
LANGUAGE_RPEFIX_LENGTH = len(LANGUAGE_PREFIX)
CURRENT_APPLICATION = 'applications/current'


class SnapshotDir(AbstractClient):
    """ Client which works with a snapshot """
    def __init__(self, path):
        """ .ctor
            Args:
                path (string): path to dir with snapshot
        """
        super(SnapshotDir, self).__init__()
        self.path = path

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
        if method != 'get':
            raise MethodIsNotSupported('Only get allowed in snapshot mode',
                                       url,
                                       params)
        try:
            return self.fetch(SnapshotDir.rewrite_path(url))
        except Exception as invalid_path:
            raise APIError(invalid_path, self, url)

    def fetch(self, path):
        """ Fetch data for path from file """
        path = '%s/%s.json' % (self.path, path)
        with open(path) as fp:
            return loads(fp.read())

    @classmethod
    def rewrite_path(cls, url):
        """ Build path from URL 
            Args:
                url (string): API url
            Returns:
                string: path in snapshot matches API URL 
        """
        if url == CURRENT_APPLICATION:
            # /application/current -> application.json
            return 'application'
        if url[0:LANGUAGE_RPEFIX_LENGTH] == LANGUAGE_PREFIX:
            # get language info /language/{locale} -> {locale}.json
            return '%s/language' % url[LANGUAGE_RPEFIX_LENGTH:]
        return url

class MethodIsNotSupported(APIError):
    """ Try to execute not GET request """
    MESSAGE = 'Method %s is not supported'
    def __init__(self, method,  url, client):
        super(MethodIsNotSupported, self).__init__(self.MESSAGE % method,
                                                   client,
                                                   url)

class SnapshotFile(SnapshotDir):
    """ .tar.gz snapshot file """
    @property
    def file(self):
        """ Open tar file on demand """
        return TarFile.open(self.path, 'r')

    def fetch(self, path):
        try:
            fp = self.file.extractfile('%s.json' % path)
            ret = loads(fp.read())
            return ret
        finally:
            if fp:
                fp.close()


def open_snapshot(path):
    """ Open snapshot file or directory
        Args:
            path (string): path to file or dir
        Returns:
            SnapshotDir|SnapshotFile
    """
    if not exists(path):
        raise Error('Snapshot %s does not exists' % path)
    if isdir(path):
        return SnapshotDir(path)
    else:
        return SnapshotFile(path)

