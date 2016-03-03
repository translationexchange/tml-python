# encoding: UTF-8
""" Test rules built-in functions """
from __future__ import absolute_import
import unittest
from tml.rules.functions import *
from tml.rules.engine import RulesEngine
from json import loads
import re
from tml.rules.parser import parse
import six
from tml.strings import to_string
default_engine = RulesEngine(SUPPORTED_FUNCTIONS) # default engine

class FunctionsTest(unittest.TestCase):
    def test_to_int(self):
        """ Test assinment to integer """
        self.assertEquals(1, to_int('1'), '1')
        self.assertEquals(100, to_int('100'), '100')
        self.assertEquals(0, to_int('0'), '0')
        with self.assertRaises(ArgumentError):
            to_int('a')
        with self.assertRaises(ArgumentError):
            to_int('1a')
        with self.assertRaises(ArgumentError):
            to_int('05')
        with self.assertRaises(ArgumentError):
            to_int('00')

    def test_to_range(self):
        self.assertEquals((0, 10), to_range('0..10'), '0..10')
        self.assertEquals((100, 500), to_range('100..500'), '100..500')
        with self.assertRaises(ArgumentError) as context:
            to_range('a..100')
        with self.assertRaises(ArgumentError) as context:
            to_range('5..b')
        with self.assertRaises(ArgumentError) as context:
            to_range('05..08')
        with self.assertRaises(InvalidRange) as context:
            to_range('8..5')

    def test_in_f(self):
        """ Test in_f implementation """
        self.assertFalse(in_f('a', 'b'), 'b in a')
        self.assertTrue(in_f('a', 'a'), 'a in a')
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

    def test_build_preg(self):
        self.assertEqual(re.I, build_flags('i'), 'Regexp i flag')
        self.assertEqual(re.I|re.M, build_flags('mi'), 'Regexp im flag')
        self.assertEquals(re.compile(six.u('\d+')), build_regexp('\d+'), '\d+')
        self.assertEquals(re.compile(six.u('[a-z]+'), re.I|re.M), build_regexp('/[a-z]+/im'), '/[a-z]+/im')
        self.assertEquals(re.compile(six.u('[a-z]+'), re.I|re.M), build_regexp('/[a-z]+/im'), '/[a-z]+/im')
        self.assertEquals(re.compile(six.u('[a-z]+')), build_regexp('/[a-z]+/'), '/[a-z]+/')

    def test_all(self):
        self.assertTrue(SUPPORTED_FUNCTIONS['all'](['male','male','male'], 'male'),'All is male')
        self.assertFalse(SUPPORTED_FUNCTIONS['all'](['male','female'],'male'),'One is not male')

    def test_any(self):
        self.assertTrue(SUPPORTED_FUNCTIONS['any'](['male','female'],'male'), 'Any is male')
        self.assertFalse(SUPPORTED_FUNCTIONS['any'](['female','female'],'male'), 'Nobody is male')

    def test_cmp(self):
        self.assertTrue(SUPPORTED_FUNCTIONS['<']('3', 10), '"3" < 10')
        self.assertFalse(SUPPORTED_FUNCTIONS['>'](date(2015, 0o1, 20), date(2015, 0o2, 22)), 'Cmp dates')

    def test_eq(self):
        self.assertTrue(f_eq(10, '10'), '10 == "10"')
        self.assertTrue(f_eq(10, 10), '10 == "10"')
        self.assertTrue(f_eq('A', 'A'), '"A" == "A"')
        self.assertFalse(f_eq(10, 'A'), '10 != "A')

    def test_regexp(self):
        self.assertFalse(SUPPORTED_FUNCTIONS['match']('/(Лев)$/','Маша'))
        self.assertTrue(SUPPORTED_FUNCTIONS['match']('/(ша)$/','Маша'))
        self.assertTrue(SUPPORTED_FUNCTIONS['match']('/(\d+)$/', 100))
        self.assertTrue(SUPPORTED_FUNCTIONS['match']('/test/i', 'TEST'), 'Test pcre flags')
        self.assertEquals('1ooo', SUPPORTED_FUNCTIONS['replace']('0', 'o', '1000'), 'Test replace')
        self.assertEquals('100o', SUPPORTED_FUNCTIONS['replace']('0$', 'o', '1000'), 'Test preg replace')
        srule = loads('{"test":"(match \'/а$/\' @value)","replace":"(replace \'/а$/\' \'е\' @value)"}')
        sdata = loads('{"value":"Маша"}')
        rule = parse(srule['test'])
        self.assertTrue(default_engine.execute(rule, sdata), 'Re supports json encoding')
        self.assertEquals(to_string("Маше"), default_engine.execute(parse(srule['replace']), sdata), 'Маша -> Маше')

    def test_atom(self):
        self.assertTrue(SUPPORTED_FUNCTIONS['atom'](1))
        self.assertTrue(SUPPORTED_FUNCTIONS['atom'](1.))
        self.assertTrue(SUPPORTED_FUNCTIONS['atom']('hi'))
        self.assertTrue(SUPPORTED_FUNCTIONS['atom'](None))
        self.assertTrue(SUPPORTED_FUNCTIONS['atom'](False))
        self.assertFalse(SUPPORTED_FUNCTIONS['atom']([]))
        self.assertFalse(SUPPORTED_FUNCTIONS['atom'](tuple()))



if __name__ == '__main__':
    unittest.main()

