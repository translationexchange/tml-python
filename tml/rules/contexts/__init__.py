# encoding: UTF-8
""" Rules variables, like @gender, @n """
from tml.exceptions import Error as BaseError
from _ctypes import ArgumentError
from .count import Count
from .number import Number
from .date import Date
from .gender import Gender
from .genders import Genders

class Value(object):
    """ String value """
    @classmethod
    def match(cls, data):
        return str(data)

class Fetcher(object):
    """ Class which get supported context """
    def __init__(self, contexts):
        """ Context fetcher
            Args:
                contexts (code, matcher)[]: list of contexts
        
        """
        self.contexts = contexts


    def get_context(self, data):
        """ Get context for data
            Args:
                data (mixed): input data
            Returns:
                (context, value in context)
        """
        for key, context in self.contexts:
            try:
                return (key, context.match(data))
            except ArgumentError:
                pass # context is not supported
        raise ArgumentError('No context for input data')

# Default fetcher:
_fetcher = Fetcher([('date', Date),
                    ('gender', Gender),
                    ('genders', Genders),
                    ('list', Count),
                    ('number', Number),
                    ('value', Value)])

def get_context(data):
    return _fetcher.get_context(data)