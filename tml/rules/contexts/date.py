# encoding: UTF-8
from _ctypes import ArgumentError
from datetime import date, datetime

class Date(date):
    """ Date context """
    supported_formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']
    @classmethod
    def match(cls, data):
        """ Check is data has a date context
            Args:
                data (mixed): data
            Throws:
                ArgumentException
            Returns:
                date
        """
        if isinstance(data, datetime):
            return data.date()
        elif isinstance(data, date):
            return data
        elif type(data) is str:
            for format in cls.supported_formats:
                try:
                    return datetime.strptime(data, format).date()
                except ValueError:
                    pass
        raise NotDate(data)

class NotDate(ArgumentError):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return 'Given data is not date: "%s"' % self.data

