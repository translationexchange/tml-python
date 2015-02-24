# encoding: UTF-8
""" Test rules built-in functions """
import unittest
from tml.rules.contexts import *

def die(object):
    raise Exception('Bad function')

class Dumn(object):
    def __str__(self):
        return 'qwerty'


class rules_variables(unittest.TestCase):
    """ Test for rules variables """
    def test_context(self):
        self.assertEquals(('date', Date(2015, 02, 23)), get_context('2015-02-23'), 'Date context')
        self.assertEquals(('gender', Gender.MALE), get_context({'name':'John', 'gender':'male'}), 'Gender context')
        self.assertEquals(('genders', [Gender.MALE, Gender.FEMALE]), get_context([{'name':'John', 'gender':'male'}, 'female']), 'Genders context')
        self.assertEquals(('list', 3), get_context([{'name':'John', 'gender':'male'}, 'female', 'no gender']), 'List context')
        self.assertEquals(('number', 12), get_context(12), 'Number context')
        self.assertEquals(('number', 12), get_context(12), 'Number context')
        self.assertEqual(('value','qwerty'), get_context(Dumn()), 'Default context')

if __name__ == '__main__':
    unittest.main()

