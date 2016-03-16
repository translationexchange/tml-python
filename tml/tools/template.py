# encoding: UTF-8
from ..strings import suggest_string, to_string
from ..session_vars import get_current_context
from ..tokenizers import DataTokenizer


class Variable(object):
    """ Fetch variable from element """
    def render(self, data):
        return to_string(suggest_string(data))

    def compile(self, context):
        return self

    def __call__(self, data):
        return self.render(data)


class Tokens(object):
    def __init__(self, tokenizer, language):
        self.tokenizer = tokenizer
        self.language = language

    def __call__(self, data):
        return self.tokenizer.execute(
            self.language,
            context=data,
            options={})

class Template(object):
    """Template compileable"""
    def __init__(self, tpl):
        self.tpl = tpl

    def compile(self, context):
        return Tokens(
            DataTokenizer.compile(self.tpl, options={}),
            context.language)

