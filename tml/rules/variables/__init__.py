# encoding: UTF-8
""" Rules variables, like @gender, @n """
from tml.exceptions import Error as BaseError


class Fetcher(object):
    """ Class to fetch rules arguments from object """
    def __init__(self, matchers):
        self.matchers = matchers

    def fetch(self, type, object):
        """ Fetch variable from object
            Args:
                type (string): variable type - key in matchers
                object (mixed): data to fetch
            Returns:
                string
        """
        if not type in self.matchers:
            raise UnsupportedType(type, object)
        try:
            return self.matchers[type](object)
        except Exception as e:
            raise UnsupportedFormat(e, type, object)

    def fetch_all(self, types, object):
        """ Fetch all variables as dict
            Args:
                types (list): types list ('@n', '@gender')
                object (mixed): object
            Retuns:
                dict
        """
        ret = {}
        for type in types:
            ret[type[1:]] = self.fetch(type, object)
        return ret


class FetcherError(BaseError):
    """ Error in argument fetcher """
    def __init__(self, type, object):
        self.type = type
        self.object = object

    def __str__(self):
        return 'Fault to fetch rules argument %s from %s' % (self.type, self.object)


class UnsupportedType(FetcherError):
    """ Variable type is not supported by fetcher """
    pass


class UnsupportedFormat(FetcherError):
    """ Matcher error """
    def __init__(self, exception, type, object):
        super(UnsupportedFormat, self).__init__(type, object)
        self.exception = exception

    def __str__(self):
        return '%s with %s: %s' % (super(UnsupportedFormat, self).__str__(),
                                   self.exception.__class__.__name__,
                                   self.exception)

