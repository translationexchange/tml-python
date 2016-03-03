# encoding: UTF-8
""" Test rules built-in functions """
from __future__ import absolute_import
import unittest
from datetime import date, datetime
from tml.rules.contexts.date import Date, NotDate
from json import loads

class DateTest(unittest.TestCase):
    """ Test date context """
    def setUp(self):
        self.d = date(2015, 0o2, 23)
        self.dt = datetime(2015, 0o2, 23, 17, 5, 0)

    def test_date(self):
        """ Test that date is match """
        self.assertEquals(self.d, Date.match(self.d), 'date object')

    def test_datetime(self):
        self.assertEquals(self.d, Date.match(self.dt), 'datetime object')

    def test_date_string(self):
        self.assertEquals(self.d, Date.match('2015-02-23'), 'date in sql format')
        self.assertEquals(self.d, Date.match(loads('{"date":"2015-02-23"}')['date']), 'date encoding')

    def test_datetime_string(self):
        self.assertEquals(self.d, Date.match('2015-02-23 17:05:00'), 'datetime in sql format')

    def test_no_int(self):
        with self.assertRaises(NotDate):
            Date.match(100)

    def test_correct_format(self):
        with self.assertRaises(NotDate):
            Date.match('23.02.2015')

if __name__ == '__main__':
    unittest.main()

