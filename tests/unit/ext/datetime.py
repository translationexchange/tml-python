from __future__ import absolute_import
from __future__ import print_function
import unittest
import pytest
from tests.mock import Client as ClientMock
import datetime
from tml.ext.datetime import translate
from tml import with_block_options, build_context
from tml.strings import to_string


@pytest.mark.usefixtures("build_context")
class TmlDateTimeTest(unittest.TestCase):

    def setUp(self):
        self.client = ClientMock.read_all()
        self.context = build_context(client=self.client)

    def test_translate(self):
        dummy_dt = datetime.datetime(year=1989, month=10, day=7)
        with with_block_options(dry=True):
            assert to_string('Friday, October 7, 1989') == translate(dummy_dt, ':verbose', {'with_leading_zero': False})
            assert to_string('10/07/1989') == translate(dummy_dt, '%m/%d/%Y', {'with_leading_zero': True})
            assert to_string('October 7th') == translate(dummy_dt, '{month_name} {days::ord}', {'with_leading_zero': False})
            assert '12:00 AM' == translate(dummy_dt, '{short_hours}:{minutes} {am_pm}')
