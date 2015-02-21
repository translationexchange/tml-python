# encoding: UTF-8
""" Test rules built-in functions """
import unittest
from tml.rules.variables import *

def die(object):
    raise Exception('Bad function')


class rules_variables(unittest.TestCase):
    """ Test for rules variables """
    def setUp(self):
        self.f = Fetcher({'@self': lambda object: object, '@len':lambda object: len(object), '@die': die}) 

    def test_fetcher(self): 
        self.assertEquals('hello', self.f.fetch('@self', 'hello'), 'Check fetcher')
        self.assertEquals(5, self.f.fetch('@len', 'hello'), 'Another fetcher')

    def test_unsupported_type(self):
        with self.assertRaises(UnsupportedType) as context:
            self.f.fetch('@ololo', 'Hello')
        self.assertEquals('@ololo', context.exception.type, 'Store wrong type')
        self.assertEquals('Hello', context.exception.object, 'Store object')

    def test_unsupported_format(self):
        with self.assertRaises(UnsupportedFormat) as context:
            self.f.fetch('@die', 'Hello')
        self.assertEquals('@die', context.exception.type, 'Store wrong type')
        self.assertEquals('Hello', context.exception.object, 'Store object')
        self.assertEquals('Bad function', context.exception.exception[0], 'Store previous exception')

    def test_fetch_all(self):
        self.assertEquals({'self':'Hello','len': 5},
                          self.f.fetch_all(['@self','@len'], 'Hello'),
                          'Fetch all')

    def test_fethc_all_error(self):
        with self.assertRaises(UnsupportedFormat) as context:
            self.f.fetch_all(['@self','@len','@die'], 'Hello')


if __name__ == '__main__':
    unittest.main()

