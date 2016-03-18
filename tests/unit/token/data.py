from __future__ import absolute_import
import unittest
import pytest
from six.moves import range
from tests.common import FakeUser, override_config
from tml.token.data import DataToken, Error
import tml.rules.options


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

    def test_substitute_tokens_with_array_values(self):
        users = [FakeUser(first_name='fn_{}'.format(i),
                          last_name='ln_{}'.format(i),
                          gender='male') for i in range(3)]
        token = DataToken.parse("Hello {users}")[0]
        self.assertEquals(token.token_value([users, ':first_name'], self.en), 'fn_0, fn_1 and fn_2')
        self.assertEquals(token.token_value([users, ':first_name', {'limit': 2, 'joiner': 'or'}], self.en), 'fn_0 or fn_1')
        self.assertEquals(token.token_value([users, '<b>{$0}</b>'], self.en), '<b>fn_0 ln_0</b>, <b>fn_1 ln_1</b> and <b>fn_2 ln_2</b>')
        self.assertEquals(token.token_value([users, {'attribute': 'first_name'}], self.en), 'fn_0, fn_1 and fn_2')
        self.assertEquals(token.token_value([users, {'property': 'first_name'}], self.en), 'fn_0, fn_1 and fn_2')

    def test_errors(self):
        dummy_user = FakeUser()
        cases = (
            {'userr': None},
            {'user': [dummy_user, ':name']},
            {'user': {'object': dummy_user, 'attribute': 'name'}},
            {'user': {'object': dummy_user, 'bad_key': str(dummy_user)}},
        )
        with override_config(strict_mode=True):
            for case in cases:
                with self.assertRaises(Error):
                    self.token.substitute(self.label, case, self.en)

