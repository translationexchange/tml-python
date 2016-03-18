from __future__ import absolute_import
# encoding: UTF-8
import unittest
import pytest
from six import iteritems
from mock import patch
from tests.common import FakeUser
from tml.strings import to_string
from tml.token.transform import TransformToken, Error, PIPE_CHAR, DBL_PIPE_CHAR
import tml.token.data



@pytest.mark.usefixtures("init_app")
class TransformTokenTest(unittest.TestCase):

    def setUp(self):
        self.app = self.init_app()
        self.en = self.app.language('en')
        self.ru = self.app.language('ru')
        self.label = "This is {user|he,she,it}"
        self.token = TransformToken.parse(self.label)[0]

    def test_parse(self):
        self.assertIsInstance(self.token, TransformToken)
        self.assertEquals(self.token.short_name, 'user')
        self.assertEquals(self.token.context_keys, [])
        self.assertEquals(self.token.case_keys, [])
        self.assertEquals(self.token.piped_params, 'he,she,it')
        self.assertEquals(self.token.pipe_separator, PIPE_CHAR)
        self.assertFalse(self.token.token_value_displayed())
        self.assertTrue(self.token.is_implied())

    def test_misc(self):
        token = TransformToken.parse("This is {user||he,she,it}")[0]
        self.assertEquals(token.piped_params, 'he,she,it')
        self.assertEquals(token.pipe_separator, DBL_PIPE_CHAR)
        self.assertTrue(token.token_value_displayed())
        self.assertFalse(token.is_implied())


    @patch('tml.token.data.is_language_cases_enabled', return_value=True)
    def test_complete_substitution(self, _):
        case_dict = {
            'This is {user|he,she,it}': [
                ({'user': FakeUser(gender='male')}, 'This is he'),
                ({'user': FakeUser(gender='female')}, 'This is she'),
                ({'user': FakeUser(gender='other')}, 'This is it')],
            'This is {user||he,she,it}': [
                ({'user': FakeUser(gender='male')}, 'This is Tom Anderson he'),
                ({'user': FakeUser(gender='female')}, 'This is Tom Anderson she'),
                ({'user': FakeUser(gender='other')}, 'This is Tom Anderson it')],
            'This is {user|male: he, female: she, other: he/she}': [
                ({'user': FakeUser(gender='male')}, 'This is he'),
                ({'user': FakeUser(gender='female')}, 'This is she'),
                ({'user': FakeUser(gender='other')}, 'This is he/she')],
            '{count||message}': [
                ({'count': 1}, '1 message'),
                ({'count': 2}, '2 messages'),],
        }
        for label, cases in iteritems(case_dict):
            token = TransformToken.parse(label)[0]
            # print label
            for case in cases:
                self.assertEquals(token.substitute(label, case[0], self.en), case[1])
