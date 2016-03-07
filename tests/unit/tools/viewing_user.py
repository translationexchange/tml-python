from __future__ import absolute_import
# encoding: UTF-8
import unittest
from tml.tools.viewing_user import get_viewing_user, set_viewing_user, reset_viewing_user
from tml.tools.template import Template
from tests.mock import Client
from tml import build_context, tr, initialize, RenderEngine
from _ctypes import ArgumentError


class ViewingUserTest(unittest.TestCase):

    def setUp(self):
        reset_viewing_user()
        RenderEngine.env_generators.append(get_viewing_user)

    def test_viewing_user(self):
        initialize(client=Client.read_all())
        set_viewing_user({'gender':'male','name':'Bond'})
        self.assertEquals('Mr', tr('honorific'))
        set_viewing_user('female')
        self.assertEquals('Ms', tr('honorific'))
        reset_viewing_user()
        self.assertEqual('Mr or Ms', tr('honorific'))

    def test_invalid_user(self):
        with self.assertRaises(ArgumentError) as c:
            set_viewing_user('zzzzz')


if __name__ == '__main__':
    unittest.main()

