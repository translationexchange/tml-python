from ..functions import IS_INT
from _ctypes import ArgumentError


class Number(object):
    """ Number context """
    @classmethod
    def match(cls, data):
        if type(data) is int:
            return data
        if type(data) is float:
            return data
        try:
            if IS_INT.match(data):
                return int(data)
        except TypeError:
            pass
        raise ArgumentError('Input data is not integer')

