# encoding: UTF-8
""" Test rules built-in functions """
import unittest
from tml.rules.contexts.genders import *

class Male(object):
    """ Male class """
    @property
    def gender(self):
        return Gender.MALE

def generator(gender, count):
    for i in range(count):
        yield gender


class NoGender(object):
    """ Class with no gender to raise error """
    pass


class genders_test(unittest.TestCase):
    def test_list(self):
        self.assertEquals([Gender.MALE, Gender.FEMALE, Gender.OTHER],
                          Genders.match([Male(), 'female', Gender(Gender.OTHER, None)]),
                          'Gender list')

    def test_generator(self):
        self.assertEquals([Gender.MALE, Gender.MALE], Genders.match(generator(Gender.MALE, 2)), 'Test generator')

    def test_not_gender(self):
        with self.assertRaises(ArgumentError):
            Genders.match([Male(),':(', Gender.MALE])

    def test_string(self):
        with self.assertRaises(ArgumentError):
            Genders.match('Hello')

    def test_not_iterable(self):
        with self.assertRaises(ArgumentError):
            Genders.match(Male())

