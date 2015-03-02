# encoding: UTF-8
""" Test rules built-in functions """
import unittest
from tml.rules import parse
from tests.mock import Client
from tml import Application
from tml.language import Language
from tml.rules.contexts import Gender
from tml.rules.case import Case
from tml.rules import default_engine

class case(unittest.TestCase):
    """ Test rules engine """
    def test_case(self):
        c = Case.from_rules([{'conditions': "(&& (= 'female' @gender) (match '/(ша)$/' @value))", "operations": "(replace '/а$/' 'и' @value)"},
                             {'conditions': "(match '/а$/' @value)", "operations": "(replace '/а$/' 'ы' @value)"}])
        self.assertEquals('Маши',
                          c.execute(Gender.female('Маша')),
                          'Маша -> Маши')
        self.assertEquals('Лены',
                          c.execute(Gender.female('Лена')),
                          'Лена -> Лены')
        self.assertEquals('Вася',
                          c.execute(Gender.female('Вася')),
                          'Вася -> Вася')


if __name__ == '__main__':
    unittest.main()

