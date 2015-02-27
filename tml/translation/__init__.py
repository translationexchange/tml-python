# encoding: UTF-8
from tml.token.parser import default_parser
from tml.token import execute_all
from hashlib import md5


class Key(object):
    """ Translation key """
    def __init__(self, language, label, description = ''):
        """ .ctor
            Args:
                label (string): tranlated string f.ex. "{name} take me {count||apple, apples}"
                description (string): translation description
                language (Language): language instance
        """
        self.label = label
        self.description = description
        self.language = language


    @property
    def key(self):
        """ Key property """
        return md5('%s;;;%s' % (self.label, self.description)).hexdigest()

