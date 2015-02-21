# encoding: UTF-8
""" Test rules built-in functions """
import unittest
from tml.rules.functions import *


class rules_functions(unittest.TestCase):
    def test_to_int(self):
        """ Test assinment to integer """
        self.assertEquals(1, to_int('1'), '1')
        self.assertEquals(100, to_int('100'), '100')
        self.assertEquals(0, to_int('0'), '0')
        with self.assertRaises(ArgumentError) as context:
            to_int('a')
        with self.assertRaises(ArgumentError) as context:
            to_int('1a')
        with self.assertRaises(ArgumentError) as context:
            to_int('05')
        with self.assertRaises(ArgumentError) as context:
            to_int('00')

    def test_to_range(self):
        self.assertEquals((0, 10), to_range('0..10'), '0..10')
        self.assertEquals((100, 500), to_range('100..500'), '100.500')
        with self.assertRaises(ArgumentError) as context:
            to_range('a..100')
        with self.assertRaises(ArgumentError) as context:
            to_range('5..b')
        with self.assertRaises(ArgumentError) as context:
            to_range('05..08')
        with self.assertRaises(ArgumentError) as context:
            to_range('8..5')

    def test_in_f(self):
        """ Test in_f implementation """
        self.assertTrue(in_f('a,b,c', 'b'), 'b in a,b,c')
        self.assertFalse(in_f('aa,bb,cc', 'a'), 'a not in aa,bb,cc')
        self.assertTrue(in_f('1,2,3', 1), '1 in 1,2,3')
        self.assertTrue(in_f('1,2,3', '3'), '"3" in 1,2,3')
        self.assertTrue(in_f('1..5', '1'), '"1" in 1..5')
        self.assertTrue(in_f('1..5', 5), '5 in 1..5')
        self.assertFalse(in_f('1..5', 6), '6 not in 1..5')
        self.assertTrue(in_f('1..5', '3'), '"3" in 1..5')
        self.assertTrue(in_f('1..5', 3), '3 in 1..5')
        self.assertTrue(in_f('1..3,5..8', 7), '7 in 1..3,5..8')

