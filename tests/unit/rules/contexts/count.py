# encoding: UTF-8
""" Test rules built-in functions """
from __future__ import absolute_import
import unittest
from tml.rules.contexts.count import *
import six


class WithLength(object):
    def __len__(self):
        return 10

class WithoutLength(object):
    pass

class CountTest(unittest.TestCase):
    """ Test count """
    def test_list(self):
        self.assertEquals(3, Count.match([1,2,3]), 'List')

    def test_tuple(self):
        self.assertEquals(2, Count.match((100, 500)), 'Tuple')

    def test_object(self):
        self.assertEquals(10, Count.match(WithLength()), 'Object with length getter')
        with self.assertRaises(ArgumentError):
            Count.match(WithoutLength())

    def test_string(self):
        with self.assertRaises(ArgumentError):
            Count.match('Hello world')
        with self.assertRaises(ArgumentError):
            Count.match(six.u('Hello world'))

    def test_dict(self):
        self.assertEquals(2, Count.match({'a':'A', 'b':'B'}), 'Count dict')

if __name__ == '__main__':
    unittest.main()

