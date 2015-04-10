# encoding: UTF-8
from . import Hashtable
from ..api.pagination import allpages
from . import Hashtable
from .translations import Dictionary
from hashlib import md5
from ..translation.missed import MissedKeys
from tml.api.client import ClientError
from tml.dictionary import TranslationIsNotExists

class SourceMissed(MissedKeys):
    def __init__(self, client, source):
        super(SourceMissed, self).__init__(client)
        self.source = source

    def as_dict(self):
        ret = super(SourceMissed, self).as_dict()
        ret.update({'source': self.source})
        return ret


class SourceDictionary(Hashtable):
    """ Dictionary of keys grouped by source """
    def __init__(self, source, language, fallback = None):
        """ .ctor 
            Args:
                source (string): source name
                lang (Language): language
                missed_keys (list): list of missed keys
        """
        self.source = source
        self.language = language
        self.missed_keys = SourceMissed(self.language.client, source)
        data = self.language.client.get(*self.api_query)
        super(SourceDictionary, self).__init__(data['results'], fallback)


    @property
    def api_query(self):
        return ('sources/%s/translations' % (md5(self.source).hexdigest()), {'locale': self.language.locale})

    def fetch(self, key):
        try:
            return super(SourceDictionary, self).fetch(key)
        except TranslationIsNotExists as e:
            self.missed_keys.append(key)
            raise e

    def __del__(self):
        self.flush()

    def flush(self):
        """ Submit all missed keys on delete """
        if self.missed_keys.submit_all():
            self.language.client.reload(*self.api_query)


