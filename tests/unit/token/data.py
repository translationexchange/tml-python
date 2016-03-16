from __future__ import absolute_import
import unittest
import pytest
from tml.token import DataToken


class FakeUser(object):

    first_name = 'Tom'
    last_name = 'Anderson'
    gender = 'male'

    def __str__(self):
        return self.first_name + " " + self.last_name


@pytest.mark.usefixtures("init_app")
class DataTokenTest(unittest.TestCase):

    def setUp(self):
        self.app = self.init_app()
        self.en = self.app.language('en')
        self.ru = self.app.language('ru')
        self.label = "Hello {user}"
        self.token = DataToken.parse(self.label)[0]

    def test_parse(self):
        self.assertIsInstance(self.token, DataToken)
        self.assertEquals(self.token.short_name, 'user')
        self.assertEquals(self.token.context_keys, [])
        self.assertEquals(self.token.case_keys, [])

    def test_substitution(self):
        dummy_user = FakeUser()
        # tr("Hello {user}", "", {'user': current_user}}
        self.assertEquals(self.token.token_value(dummy_user, self.en), str(dummy_user))

        # tr("Hello {user}", "", {'user': [current_user, current_user.name]}}
        self.assertEquals(self.token.token_value([dummy_user, dummy_user.first_name], self.en), dummy_user.first_name)

        # tr("Hello {user}", "", {:user => [current_user, ':name']}}
        self.assertEquals(self.token.token_value([dummy_user, ':first_name'], self.en), dummy_user.first_name)

        # tr("Hello {user}", "", {'user': {'object': current_user, 'value': current_user.name}]}}
        self.assertEquals(self.token.token_value({'object': dummy_user, 'value': str(dummy_user)}, self.en), str(dummy_user))

        # tr("Hello {user}", "", {'user': {'object': current_user, 'attribute': 'first_name'}]}}
        self.assertEquals(self.token.token_value({'object': dummy_user, 'attribute': 'first_name'}, self.en), dummy_user.first_name)

        self.assertEquals(self.token.token_value({'object': dummy_user, 'property': 'last_name'}, self.en), dummy_user.last_name)

    def test_complete_substitution(self):
        dummy_user = FakeUser()
        cases = (
            ({'user': dummy_user}, 'Hello Tom Anderson'),
            ({'user': [dummy_user, dummy_user.first_name]}, 'Hello Tom'),
            ({'user': [dummy_user, ':last_name']}, 'Hello Anderson'),
            ({'user': {'object': dummy_user, 'attribute': 'first_name'}}, 'Hello Tom'),
            ({'user': {'object': dummy_user, 'value': str(dummy_user)}}, 'Hello Tom Anderson')
        )
        for pair in cases:
            self.assertEquals(self.token.substitute(self.label, pair[0], self.en), pair[1])


