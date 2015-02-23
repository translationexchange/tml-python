from .gender import Gender
from _ctypes import ArgumentError

class Count(object):
    """ List having count """
    @classmethod
    def match(cls, data):
        """ Check is data list of genders """
        if type(data) in (list, tuple):
            return len(data)
        if type(data) in (str, unicode):
            raise ArgumentError('String has no count')
        if hasattr(data, '__len__'):
            return len(data)
        raise ArgumentError('Data has no length')

