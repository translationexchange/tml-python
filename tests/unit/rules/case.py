# encoding: UTF-8
""" Test rules built-in functions """
import unittest
from tml.rules import parse
from tests.mock import Client
from tml import Application
from tml.language import Language
from tml.rules.contexts import Gender
from tml.rules.case import Case
from tml.rules.parser import ParseError

class CaseTest(unittest.TestCase):
    """ Test rules engine """
    def setUp(self):
        self.rules = [{'conditions': "(&& (= 'female' @gender) (match '/(ша)$/' @value))", "operations": "(replace '/а$/' 'и' @value)"},
                      {'conditions': "(match '/а$/' @value)", "operations": "(replace '/а$/' 'ы' @value)"}]
        self.invalid_rules = [{'conditions':'(mode 3 @value))', 'operations': ''}]


    def test_case(self):
        c = Case.from_rules(self.rules)
        self.assertEquals('Маши',
                          c.execute(Gender.female('Маша')),
                          'Маша -> Маши')
        self.assertEquals('Лены',
                          c.execute(Gender.female('Лена')),
                          'Лена -> Лены')
        self.assertEquals('Вася',
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
        self.assertEquals(['gen2','gen'], cases.keys(), 'Return only valid')
        self.assertEquals(str(context.exception), str(errors['err']), 'Store errors in errors')
        self.assertEquals(['err2','err'], errors.keys(), 'Store all error')

if __name__ == '__main__':
    unittest.main()

