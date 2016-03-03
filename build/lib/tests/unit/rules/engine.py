# encoding: UTF-8
""" Test rules built-in functions """
from __future__ import absolute_import
import unittest
from mock import patch
from tml.rules.engine import *
from tml.rules.functions import SUPPORTED_FUNCTIONS
from tml.rules.parser import parse

def die_op():
    raise Exception('dummy exception')


class EngineTest(unittest.TestCase):
    """ Test of rules engine """
    def setUp(self):
        """ Use mock engine """
        self.engine = RulesEngine(SUPPORTED_FUNCTIONS)

    def test_number_rules(self):
        self.assertEquals(
                        1,
                        self.engine.execute(
                                       parse('(mod @n 10)'),
                                       {'n': 1}),
                        '@n = 1 -> (mod @n 10)')
        self.assertTrue(
                        self.engine.execute(
                                       parse('(= 1 @n)'),
                                       {'n': 1}),
                        '@n = 1 -> (= 1 @n)')

        self.assertTrue(
                        self.engine.execute(
                                       parse('(= 1 (mod @n 10))'),
                                       {'n': 1}),
                        '@n = 1 -> (= 1 (mod @n 10))')

        self.assertTrue(
                        self.engine.execute(
                                       parse('(&& (= 1 (mod @n 10)) (!= 11 (mod @n 100)))'),
                                       {'n': 1}))

    def test_execution(self):
        """ Test rules engine"""
        self.assertEquals(5, self.engine.execute(['+', '2', '3'], {}), '(+ 2 3)')
        
    def test_arguments(self):
        """ Pass arguments """
        self.assertEquals(5, self.engine.execute(['+', '@a', '@b'], {'a':2, 'b':3}), '(+ @a @b)')
        self.assertTrue(
            self.engine.execute(
                parse('(&& (= @a (mod @n @b)) (!= @c (mod @n @d)))'),
                    {'n': 1, 'a': 1, 'b': 10, 'c': 2, 'd': 100}))


    def test_inner(self):
        """ Inner expression """
        self.assertEquals(3, self.engine.execute(['mod', ['+', '8', '5'], '10'], {}), '(mod (+ 8 5) 10)')
        self.assertEquals(3, self.engine.execute(['mod', ['+', '@a', '5'], '@b'], {'a':18, 'b':10}), '(mod (+ @a 5) @b)')

    def test_function_not_suported(self):
        with self.assertRaises(FunctionDoesNotExists) as context:
            self.engine.execute(['xor', '2', '3'], {})

    def test_argument_does_not_exists(self):
        with self.assertRaises(ArgumentDoesNotExists) as context:
            self.engine.execute(['+', '@e', '3'], {})
        self.assertEquals('@e', context.exception.argument_name, 'Store argument name')
        self.assertEquals(1, context.exception.part_number, 'In first argument')

    @patch.dict(SUPPORTED_FUNCTIONS, {'die': die_op})
    def test_function_error(self):
        """ Check that engine handle function error """
        with self.assertRaises(FunctionCallFault) as context:
            self.engine.execute(['die'], {})
        with self.assertRaises(FunctionCallFault) as context:
            # Pass invalid argument:
            self.engine.execute(['mod', 'a', '10'], {})
        self.assertEquals(ValueError, context.exception.exception.__class__, 'Store original exception')
        with self.assertRaises(FunctionCallFault) as context:
            # Pass wrong count argument:
            self.engine.execute(['mod', '1', '10', '100'], {})
        self.assertEquals(TypeError, context.exception.exception.__class__, 'Store original exception')

    @patch.dict(SUPPORTED_FUNCTIONS, {'die': die_op})
    def test_inner_function_call(self):
        with self.assertRaises(InnerExpressionCallFault) as context:
            self.engine.execute(['mod', '10', ['die']], {})
        self.assertEquals(FunctionCallFault, context.exception.parent_error.__class__, 'Handle information about original error')
        self.assertEquals(2, context.exception.part_number, 'Store part number')

    def test_compare(self):
        engine = RulesEngine(SUPPORTED_FUNCTIONS)
        self.assertTrue(engine.execute(['<', '@value', '10'], {'value': 8}), '8 < 10')
        self.assertFalse(engine.execute(['<', '@value', '7'], {'value': 8}), '! 8 < 7')
        self.assertTrue(engine.execute(['<', '7', '@value'], {'value': 8}), '7 < 8')
        q = parse('(&& (< 3 @value) (> 12 @value))')
        self.assertTrue(engine.execute(q, {'value': 8}))
        self.assertFalse(engine.execute(q, {'value': 3}))
        self.assertFalse(engine.execute(q, {'value': 14}))


if __name__ == '__main__':
    unittest.main()

