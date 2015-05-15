# encoding: UTF-8
""" Test rules built-in functions """
from __future__ import absolute_import
import unittest
from tml.rules.contexts.gender import *

class Male(object):
    """ Male class """
    @property
    def gender(self):
        return Gender.MALE

class NoGender(object):
    """ Class with no gender to raise error """
    pass


class GenderTest(unittest.TestCase):
    def test_gender(self):
        """ Test gender mathcher """
        self.assertEquals(Gender.MALE, Gender.match('male'), 'male')
        self.assertEquals(Gender.FEMALE, Gender.match('female'), 'female')
        self.assertEquals(Gender.OTHER, Gender.match('other'), 'other')
        self.assertEquals(Gender.MALE, Gender.match({'gender':'male'}), '{gender:male}')
        self.assertEquals(Gender.MALE, Gender.match(Male()), 'object instance with gender property')
        self.assertEquals(Gender.FEMALE, Gender.match(Gender('female', 'Eva')), 'object instance with gender property')

    def test_invalid_gender(self):
        with self.assertRaises(ArgumentError):
            Gender.match('Hello world')
        with self.assertRaises(ArgumentError):
            Gender.match(None)

    def test_key_not_exists(self):
        with self.assertRaises(ArgumentError):
            Gender.match({'message':'Hello world'})

    def test_attribute_not_exists(self):
        with self.assertRaises(ArgumentError):
            Gender.match(NoGender())

    def test_invalid_type(self):
        with self.assertRaises(ArgumentError):
            Gender.match([1,2,4])


if __name__ == '__main__':
    unittest.main()

