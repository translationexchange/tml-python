# encoding: UTF-8
from ..strings import suggest_string, to_string
from ..token import parser, execute_all

class Variable(object):
    """ Fetch variable from element """
    def render(self, data):
        return to_string(suggest_string(data))

    def compile(self, context):
        return self

    def __call__(self, data):
        return self.render(data)


class Tokens(object):
    def __init__(self, tokens):
        self.tokens = tokens

    def __call__(self, data):
        return execute_all(self.tokens, data, {})


class Template(object):
    """Template compileable"""
    def __init__(self, tpl):
        self.tpl = tpl

    def compile(self, context):
        return Tokens(parser.default_parser.parse(self.tpl, context.language))

