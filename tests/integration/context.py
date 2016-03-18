from __future__ import absolute_import
# encoding: UTF-8
import unittest

from tml.context import AbstractContext
from ..common import FakeLanguage


class ContextTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_abstract_context_spec(self):
        context = AbstractContext(FakeLanguage())
        self.assertIsInstance(context.language, FakeLanguage, '_language is set')


if __name__ == '__main__':
    unittest.main()

