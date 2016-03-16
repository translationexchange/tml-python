import unittest
import pytest
from tests.common import FakeUser
from tml.tokenizers import DataTokenizer
from tml.token.transform import PIPE_CHAR


@pytest.mark.usefixtures("init_app")
class DataTokenizerTest(unittest.TestCase):

    def setUp(self):
        self.app = self.init_app()
        self.en = self.app.language('en')
        self.ru = self.app.language('ru')

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

        dt = DataTokenizer('{test}, {test:one}, {test::two}, {test|message, messages}, {gender||male: he, female: she}')
        self.assertEquals(len(dt.tokens), 5)
        for token in dt.tokens:
            if token.context_keys:
                self.assertEquals(token.context_keys, ['one'])
            if token.case_keys:
                self.assertEquals(token.case_keys, ['two'])
                self.assertEquals(token.name(dict(parens=True, case_keys=True)), '{test::two}')
            if hasattr(token, 'pipe_separator'):
                if token.pipe_separator == PIPE_CHAR: # |
                    self.assertEquals(token.piped_params, 'message, messages')
                else:  # ||
                    self.assertEquals(token.piped_params, 'male: he, female: she')

    def test_substitute(self):
        label = "{user:gender|He,She} has {count||message}."
        cases = (
            ({'user': FakeUser(gender='male'), 'count': 1}, 'He has 1 message.'),
            ({'user': FakeUser(gender='female'), 'count': 5}, 'She has 5 messages.'),
            ({'user': FakeUser(gender='other'), 'count': 5}, 'He/She has 5 messages.'),
        )
        for case in cases:
            dt = DataTokenizer(label, context=case[0])
            self.assertEquals(dt.substitute(self.en), case[1])
