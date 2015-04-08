# encoding: UTF-8
from .client import APIError, Client as BaseClient
from tarfile import TarFile
from json import loads
from os.path import isdir, exists
from ..exceptions import Error

LANGUAGE_PREFIX = 'languages/'
LANGUAGE_RPEFIX_LENGTH = len(LANGUAGE_PREFIX)
CURRENT_APPLICATION = 'applications/current'


class SnapshotDir(BaseClient):
    """ Client which works with a snapshot """
    def __init__(self, path):
        """ .ctor
            Args:
                path (string): path to dir with snapshot
        """
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
            raise MethodIsNotSupported('Only get allowed in snapshot mode', url, params)
        try:
            return self.fetch(self.rewrite_path(url))
        except Exception as e:
            raise APIError(e, self, url)

    def fetch(self, path):
        """ Fetch data for path from file """
        path = '%s/%s.json' % (self.path, path)
        with open(path) as fp:
            return loads(fp.read())

    def rewrite_path(self, url):
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
    def __init__(self, method,  url, client):
        super(MethodIsNotSupported, self).__init__('Method %s is not supported' % method, client, url)

class SnapshotFile(SnapshotDir):
    """ .tar.gz snapshot file """
    def __init__(self, path):
        self.path = path

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
            try:
                fp.close()
            except Exception:
                pass


def open_snapshot(path):
    if not exists(path):
        raise Error('Snapshot %s does not exists' % path)
    if isdir(path):
        return SnapshotDir(path)
    else:
        return SnapshotFile(path)

