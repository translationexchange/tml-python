from __future__ import absolute_import
from __future__ import print_function
import unittest
import pytest
from mock import patch
from tests.mock import Client as ClientMock
from tests.common import FakeUser
import datetime
from tml.ext.str import translate
from tml import with_block_options, build_context
from tml.strings import to_string


@pytest.mark.usefixtures("build_context")
class TmlStrTest(unittest.TestCase):

    def setUp(self):
        self.client = ClientMock.read_all()
        self.context = build_context(client=self.client)

    def test_translate(self):
        with with_block_options(dry=True):
            assert to_string("Hello world") == translate("Hello world")
            assert to_string("This belongs to him") == translate("This belongs to {user|him,her}", data={'user': FakeUser(first_name="John", gender='male')})

