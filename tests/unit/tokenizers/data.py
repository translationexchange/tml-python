import unittest
import pytest
from tml.tokenizers import DataTokenizer

class DataTokenizerTest(unittest.TestCase):

    def test_initialize(self):
        dt = DataTokenizer('Hello World')
        self.assertEquals(dt.tokens, [])
        dt = DataTokenizer('foo {bar}')
        self.assertEquals(len(dt.tokens), 1)
        self.assertEquals(dt.tokens[0].name(), 'bar')
        self.assertEquals(dt.tokens[0].name(dict(parens=True)), '{bar}')

        dt = DataTokenizer('Dear {user:gender}')
        self.assertEquals(len(dt.tokens), 1)
        self.assertEquals(dt.tokens[0].name(), 'user')
        self.assertEquals(dt.tokens[0].name(dict(parens=True)), '{user}')
        self.assertEquals(dt.tokens[0].context_keys, ['gender'])
        self.assertEquals(dt.tokens[0].name(dict(parens=True, context_keys=True)), '{user:gender}')

        dt = DataTokenizer('{test}, {test:one}, {test::two}')
        self.assertEquals(len(dt.tokens), 3)
        for token in dt.tokens:
            if token.context_keys:
                self.assertEquals(token.context_keys, ['one'])
            if token.case_keys:
                self.assertEquals(token.case_keys, ['two'])
                self.assertEquals(token.name(dict(parens=True, case_keys=True)), '{test::two}')
