# encoding: UTF-8
""" Test rules built-in functions """
from __future__ import absolute_import
import unittest
from tml.rules import parse
from tests.mock import Client
from tml import Application
from tml.language import Language
from tml.rules.contexts import Gender
from tml.rules.case import Case, LazyCases
from tml.rules.parser import ParseError
from tml.strings import to_string

class CaseTest(unittest.TestCase):
    """ Test rules engine """
    def setUp(self):
        self.rules = [{
            "conditions": to_string("(&& (= 'female' @gender) (match '/(ша)$/' @value))"),
            "operations": to_string("(replace '/а$/' 'и' @value)")},{
            "conditions": to_string("(match '/а$/' @value)"),
            "operations": to_string("(replace '/а$/' 'ы' @value)")}]
        self.invalid_rules = [{
            "conditions": "(mode 3 @value))", "operations": ""}]


    def test_case(self):
        c = Case.from_rules(self.rules)
        self.assertEquals(to_string('Маши'),
                          c.execute(Gender.female(to_string('Маша'))),
                          'Маша -> Маши')
        self.assertEquals(to_string('Лены'),
                          c.execute(Gender.female('Лена')),
                          'Лена -> Лены')

        self.assertEquals(to_string('Вася'),
                          c.execute(Gender.female('Вася')))

    @property
    def data(self):
        return {'gen': {'rules': self.rules},
                'err':{'rules': self.invalid_rules},
                'gen2':{'rules':self.rules},
                'err2':{'rules':self.invalid_rules}}


    def test_from_data(self):
        data = self.data
        with self.assertRaises(ParseError) as context:
            # Unsafe call raises exceptions
            Case.from_data(data, False)
        cases, errors = Case.from_data(data, True)
        self.assertEquals(Case, type(cases['gen']), 'return get Case')
        cases_keys = list(cases.keys())
        cases_keys.sort()
        self.assertEquals(['gen', 'gen2'], cases_keys, 'return only valid')
        self.assertEquals(str(context.exception), str(errors['err']), 'Store errors in errors')
        errors_keys = list(errors.keys())
        errors_keys.sort()
        self.assertEquals(['err', 'err2'], errors_keys , 'store all error')

    def test_lazy(self):
        """ Test lazy case """
        cases = LazyCases(self.data)
        self.assertEqual(4, len(cases), 'all rules is in case')
        self.assertEqual(cases.cache, {}, 'really lazy')
        self.assertEquals(Case, type(cases['gen']), 'good case (gen)')
        self.assertEquals(Case, type(cases['gen2']), 'another good case (gen)')
        self.assertTrue(len(cases.cache) > 0, 'cases evaluated')
        with self.assertRaises(ParseError) as context:
            # Error case
            cases['err']

    def test_acceptence_ordinal(self):
        rules = [{
            'conditions': '(= 1 @value)',
            'operations': "(replace 1 'first' @value)"
        }, {
            'conditions': '(= 2 @value)',
            'operations': "(replace 2 'second' @value)"
        }, {
            'conditions': '(= 3 @value)',
            'operations': "(replace 3 'third' @value)"
        }]
        test_cases = (
            ('first', '1'),
            ('second', '2'),
            ('third', '3'),
            ('4', '4')
        )
        case = Case.from_rules(rules)
        for expected, val in test_cases:
            self.assertEqual(expected, case.apply({'value': val}))

if __name__ == '__main__':
    unittest.main()

