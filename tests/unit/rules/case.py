# encoding: UTF-8
""" Test rules built-in functions """
from __future__ import absolute_import
import unittest
from tml.rules import parse
from tests.mock import Client
from tml import Application
from tml.language import Language
from tml.rules.contexts import Gender
from tml.rules.case import Case
from tml.rules.parser import ParseError
from tml.strings import to_string

class CaseTest(unittest.TestCase):
    """ Test rules engine """
    def setUp(self):
        self.rules = [{'conditions': to_string("(&& (= 'female' @gender) (match '/(ша)$/' @value))"),
                       "operations": to_string("(replace '/а$/' 'и' @value)")},
                      {'conditions': to_string("(match '/а$/' @value)"),
                       "operations": to_string("(replace '/а$/' 'ы' @value)")}]
        self.invalid_rules = [{'conditions':'(mode 3 @value))', 'operations': ''}]


    def test_case(self):
        c = Case.from_rules(self.rules)
        self.assertEquals(to_string('Маши'),
                          c.execute(Gender.female(to_string('Маша'))),
                          'Маша -> Маши')
        self.assertEquals(to_string('Лены'),
                          c.execute(Gender.female('Лена')),
                          'Лена -> Лены')
        self.assertEquals(to_string('Вася'),
                          c.execute(Gender.female('Вася')),
                          'Вася -> Вася')

    def test_from_data(self):
        data = {'gen': {'rules': self.rules},
                'err':{'rules': self.invalid_rules},
                'gen2':{'rules':self.rules},
                'err2':{'rules':self.invalid_rules}}
        with self.assertRaises(ParseError) as context:
            # Unsafe call raises exceptions
            Case.from_data(data, False)
        cases, errors = Case.from_data(data, True)
        self.assertEquals(Case, type(cases['gen']), 'Return get Case')
        cases_keys = list(cases.keys())
        cases_keys.sort()
        self.assertEquals(['gen', 'gen2'], cases_keys, 'Return only valid')
        self.assertEquals(str(context.exception), str(errors['err']), 'Store errors in errors')
        errors_keys = list(errors.keys())
        errors_keys.sort()
        self.assertEquals(['err', 'err2'], errors_keys , 'Store all error')

if __name__ == '__main__':
    unittest.main()

