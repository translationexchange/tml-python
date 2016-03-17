from __future__ import absolute_import
# encoding: UTF-8
from ..token import SUPPORTED_TOKENS

__author__ = 'xepa4ep'


class DataTokenizer(object):

    text = None
    context = None
    tokens = None
    options = None

    SUPPORTED_TOKENS = SUPPORTED_TOKENS

    def __init__(self, text, context=None, options=None):
        self.text = text
        self.context = context if context is not None else {}
        self.options = options if options is not None else {}
        self.tokens = []
        self.tokenize()

    def tokenize(self):
        ret = set()
        for token_class in DataTokenizer.SUPPORTED_TOKENS:
            ret |= set(token_class.parse(self.text))   # just unique
        self.tokens = list(ret)
        return self.tokens   # for testing reasons

    def token_allowed(self, token):
        if not self.options.get('allowed_tokens', None):
            return True
        return self.options['allowed_tokens'].get(token, None) is not None

    def substitute(self, language, options=None):
        options = options if options is not None else {}
        label = self.text
        for token in self.tokens:
            if not self.token_allowed(token):
                continue
            label = token.substitute(label, self.context, language, options)
        return label
