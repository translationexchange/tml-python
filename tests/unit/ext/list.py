# encoding: UTF-8
from __future__ import absolute_import
from __future__ import print_function
import unittest
import pytest
from mock import patch
from tests.mock import Client as ClientMock
from tests.common import FakeUser
import datetime
from tml.ext.list import translate, translate_and_join, translate_sentence, tro
from tml import with_block_options
from tml.strings import to_string


@pytest.mark.usefixtures("build_context")
class TmlListTest(unittest.TestCase):

    def setUp(self):
        self.client = ClientMock.read_all()
        self.context = self.build_context(client=self.client, skip=True)

    def test_translate_and_join(self):
        assert to_string('Тест, Тест') == translate_and_join(['Test', 'Test'])
        assert to_string('Тест + Тест') == translate_and_join(['Test', 'Test'], separator=' + ')

    def test_translate_sentence(self):
        assert to_string('Тест') == translate_sentence(['Test'])
        assert to_string('Тест, Тест и Тест') == translate_sentence(['Test', 'Test', 'Test'], options={'joiner': 'and', 'separator': ', '})

    def test_tro(self):
        assert [['Test', to_string('Тест')]] == tro(['Test'])
        assert [['test', to_string('Тест')], ['and', to_string('and')]] == tro([['test', 'Test'], ['and', 'and']])
