# encoding: UTF-8
from ..strings import suggest_string, to_string


class Variable(object):
    """ Fetch variable from element """
    def render(self, data):
        return to_string(suggest_string(data))

    def __call__(self, data):
        return self.render(data)

