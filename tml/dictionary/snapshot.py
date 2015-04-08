# encoding: UTF-8
from . import Hashtable
from ..api.client import APIError

class SnapshotDictionary(Hashtable):
    """ .ctor """
    def __init__(self, source, language, fallback = None):
        try:
            data = language.client.get('%s/sources/%s' % (language.locale, source))
            super(SnapshotDictionary, self).__init__(data['results'])
        except Exception:
            print 'wtf?'
            super(SnapshotDictionary, self).__init__({})

