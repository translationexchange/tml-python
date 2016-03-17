from __future__ import absolute_import
# encoding: UTF-8
import unittest
import pytest
from mock import patch
from tests.common import FakeUser, override_config
from tml.strings import to_string
from tml.token.method import MethodToken, Error
import tml.token.data


@pytest.mark.usefixtures("init_app")
class MethodTokenTest(unittest.TestCase):

    def setUp(self):
        self.app = self.init_app()
        self.en = self.app.language('en')
        self.ru = self.app.language('ru')
        self.label = "Hello {user.first_name}"
        self.token = MethodToken.parse(self.label)[0]

    def test_parse(self):
        self.assertIsInstance(self.token, MethodToken)
        self.assertEquals(self.token.short_name, 'user.first_name')
        self.assertEquals(self.token.key, 'user')
        self.assertEquals(self.token.object_method_name, 'first_name')
        self.assertEquals(self.token.context_keys, [])
        self.assertEquals(self.token.case_keys, [])

    def test_substitution(self):
        dummy_user = FakeUser()
        self.assertEquals(self.token.token_value(dummy_user, self.en), dummy_user.first_name)

    @patch('tml.token.data.is_language_cases_enabled', return_value=True)
    def test_with_cases(self, _):
        dummy_user = FakeUser(first_name='Маша')
        token = MethodToken.parse("Hello {user.first_name::dat}")[0]
        self.assertEquals(token.token_value(dummy_user, self.ru), to_string('Маше'))

    def test_errors(self):
        dummy_user = FakeUser()
        token = MethodToken.parse("Hello {user.name}")[0]
        cases = (
            {'userr': None},
        )
        with override_config(strict_mode=True):
            for case in cases:
                with self.assertRaises(Error):
                    token.substitute(self.label, case, self.en)

