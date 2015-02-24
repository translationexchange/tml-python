# encoding: UTF-8
""" Test rules built-in functions """
import unittest
from tml.rules.engine import *
from tml.rules.functions import SUPPORTED_FUNCTIONS
from tml.rules.parser import parse

def die():
    raise Exception('Die')

class rules_engine(unittest.TestCase):
    """ Test of rules engine """
    def setUp(self):
        """ Use mock engine """
        self.engine = RulesEngine({'sum': lambda a, b: int(a) + int(b),
                                   'mod': lambda a, b: int(a) % int(b),
                                   'die': die})
    
    def test_execution(self):
        """ Test rules engine"""
        self.assertEquals(5, self.engine.execute(['sum', '2', '3'], {}), '(sum 2 3)')

    def test_arguments(self):
        """ Pass arguments """
        self.assertEquals(5, self.engine.execute(['sum', '@a', '@b'], {'a':2, 'b':3}), '(sum @a @b)')

    def test_inner(self):
        """ Inner expression """
        self.assertEquals(3, self.engine.execute(['mod', ['sum', '8', '5'], '10'], {}), '(mod (sum 8 5) 10)')
        self.assertEquals(3, self.engine.execute(['mod', ['sum', '@a', '5'], '@b'], {'a':18, 'b':10}), '(mod (sum @a 5) @b)')

    def test_function_not_suported(self):
        with self.assertRaises(FunctionDoesNotExists) as context:
            self.engine.execute(['xor', '2', '3'], {})

    def test_argument_does_not_exists(self):
        with self.assertRaises(ArgumentDoesNotExists) as context:
            self.engine.execute(['sum', '@e', '3'], {})
        self.assertEquals('@e', context.exception.argument_name, 'Store argument name')
        self.assertEquals(1, context.exception.part_number, 'In first argument')

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

