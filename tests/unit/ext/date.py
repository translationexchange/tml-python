import unittest
import pytest
from tests.mock import Client as ClientMock
from tml.ext.date import tmldate
from tml import with_block_options, build_context
from tml.strings import to_string


@pytest.mark.usefixtures("build_context")
class TmlDateTest(unittest.TestCase):

    def setUp(self):
        self.client = ClientMock.read_all()
        self.context = build_context(client=self.client)

    def test_spec(self):
        dummy_date = tmldate(year=1989, month=10, day=07)
        assert hasattr(dummy_date, 'translate') and callable(dummy_date.translate), '`translate` method is defined and set'


    def test_translate(self):
        with with_block_options(dry=True):
            dummy_date = tmldate(year=1989, month=10, day=07)
            assert to_string('Friday, October 7, 1989') == dummy_date.translate(':verbose', {'with_leading_zero': False})
            assert to_string('10/07/1989') == dummy_date.translate('%m/%d/%Y', {'with_leading_zero': True})
            assert to_string('October 7th') == dummy_date.translate('{month_name} {days::ord}', {'with_leading_zero': False})
