# encoding: UTF-8
""" Test rules built-in functions """
from __future__ import absolute_import
import unittest
from tml.rules import *
from unittest import case


class RulesTest(unittest.TestCase):
    """ Test for rules case """
    def test_conditions(self):
        case = ContextRules([
                     (['=','@value','a'],['quote','A']), # if value = a return A
                     (['=','@value','b'],['quote','B'])], # if value == b return B
                    ['quote','@value']) # in the default case return value
        self.assertEquals('A', case.apply({'value':'a'}),'if value = a return A')
        self.assertEquals('B', case.apply({'value':'b'}),'elif value == b return B')
        self.assertEquals('c', case.apply({'value':'c'}),'else return value')

    def test_rules_operations(self): 
        case = ContextRules.from_rules({
            'good_morning': {
                'conditions': '(&& (< @time 12) (> @time 3))',
                'operations': '(quote "Good morning")'},
            'good_evening': {
                'conditions':'(&& (< @time 24) (> @time 16))',
                'operations':'(quote  "Good evening")'},
            'hello':{'operations':'(quote Hello)'}})
        self.assertEquals('good_morning', case.apply({'time': 8}),'Good morning at 8AM')
        self.assertEquals('good_evening', case.apply({'time': 19}),'Good evening at 7PM')
        self.assertEquals('hello', case.apply({'time': 1}),'Hello by default')

    def test_select(self):
        case = ContextRules.from_rules({
            'one':{'conditions':'(= @value 1)'},
            'two':{'conditions':'(= @value 2)'},
            'more_than_ten':{'conditions':'(> @value 10)'},
            'another':{}})
        self.assertEquals('one', case.apply({'value': 1}))
        self.assertEquals('two', case.apply({'value': 2}))
        self.assertEquals('more_than_ten', case.apply({'value': 12}))
        self.assertEquals('another', case.apply({'value': 3}))


if __name__ == '__main__':
    unittest.main()

