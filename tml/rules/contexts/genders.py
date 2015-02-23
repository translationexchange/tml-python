from .gender import Gender
from _ctypes import ArgumentError

class Genders(object):
    @classmethod
    def match(cls, data):
        """ Check is data list of genders """
        if type(data) is str:
            raise ArgumentError('String is not genders list', data)
        
        try:
            ret = []
            for el in data:
                ret.append(Gender.match(el))
            return ret
        except TypeError:
            raise ArgumentError('Not iterable data', data)

