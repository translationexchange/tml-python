# encoding: UTF-8
""" Test rules built-in functions """
from __future__ import absolute_import
import unittest
from tml.rules.contexts.number import *
import six


class MyClass(object):
    def __len__(self):
        return 10

class WithoutLength(object):
    pass

class NumberTest(unittest.TestCase):
    """ Test count """
    def test_int(self):
        self.assertEquals(3, Number.match(3), 'Int')

    def test_tuple(self):
        self.assertEquals(3.2, Number.match(3.2), 'Float')

    def test_object(self):
        with self.assertRaises(ArgumentError):
            Number.match(MyClass())

    def test_string(self):
        self.assertEquals(100, Number.match('100'), '100')
        with self.assertRaises(ArgumentError):
            Number.match('Hello world')
        self.assertEquals(200, Number.match(six.u('200')), 'u200')
        with self.assertRaises(ArgumentError):
            Number.match(six.u('Hello world'))

if __name__ == '__main__':
    unittest.main()

