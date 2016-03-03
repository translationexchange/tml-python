# encoding: UTF-8
""" Test rules built-in functions """
from __future__ import absolute_import
import unittest
from tml.rules.parser import *


class ParserTest(unittest.TestCase):
    """ Test rules engine """
    def test_parser(self):
        """ Check is parser works correct """
        self.assertEquals(
                          ['mod', '10', '5'],
                          parse('(mod 10 5)'),
                          'Test parse')
        self.assertEquals(['mod',['+', '2', 'PI'], '5'],
                          parse('(mod (+ 2 PI) 5)'),
                          'Parse incapsulated')
        self.assertEquals(['mod','5', ['+', '2', 'PI']],
                          parse('(mod 5 (+ 2 PI))'),
                          'Parse incapsulated end')
        self.assertEquals(['mod','5', ['+', '2', ['div', '9', '3']]],
                          parse('(mod 5 (+ 2 (div 9 3)))'),
                          '3 level')
        self.assertEquals([['userfunction', 'name'],'a','b'],
                          parse('((userfunction name) a b)'),
                          'Userfunction support')
        self.assertEquals(['upper','Quoted text with (braces)'],
                          parse('(upper "Quoted text with (braces)")'),
                          'Parse quoted')
        self.assertEquals(['hello','world'],
                  parse('(hello   world)'),
                  'Ignore multispace')
        self.assertEquals(['quote', '@value'], parse('@value'), '@value')
        self.assertEquals(['upper','Single "quotes"'],
                          parse("(upper 'Single \"quotes\"')"),
                          'Single quotes')
        self.assertEquals(['mod', '1', ['+', '3', ['div', '6', '3']]],
                          parse('(mod  1 (  + 3 (div   6 3) )  )'),
                          'double space')

    def test_errors(self):
        # Check parse errrors:
        with self.assertRaises(ParseError) as context:
           parse('(hello')
        self.assertEquals(ParseError.INVALID_SYNTAX, context.exception.code, 'No open brace')
        self.assertEquals(5, context.exception.pos, 'Close bracket')

        with self.assertRaises(ParseError) as context:
           parse('hello')
        self.assertEquals(ParseError.INVALID_SYNTAX, context.exception.code, 'No close brace')
        self.assertEquals(0, context.exception.pos, 'Open bracket')

        with self.assertRaises(ParseError) as context:
           parse('(no"quote")')
        self.assertEquals(ParseError.INVALID_SYNTAX, context.exception.code, 'Unexpected quote')
        self.assertEquals(3, context.exception.pos, 'Unexpected quote pos')

        with self.assertRaises(ParseError) as context:
           parse('(quote "not closed)')
        self.assertEquals(ParseError.QUOTE_IS_NOT_CLOSED, context.exception.code, 'Quote not closed')
        self.assertEquals(7, context.exception.pos, 'Quote is not closed pos')

        with self.assertRaises(ParseError) as context:
           parse('(no ) brace)')
        self.assertEquals(ParseError.UNEXPECTED_EXPRESSION_FINISH, context.exception.code, 'Unexpected brace')
        self.assertEquals(4, context.exception.pos, 'Unexpected brace pos')

        with self.assertRaises(ParseError) as context:
           parse('(unexpected (close (brace inside))) deep)')
        self.assertEquals(ParseError.UNEXPECTED_EXPRESSION_FINISH, context.exception.code, 'Unexpected brace')

        with self.assertRaises(ParseError) as context:
           parse('(not (closed (expression))')
        self.assertEquals(ParseError.EXPRESSION_IS_NOT_CLOSED, context.exception.code, 'Not closed quote')
        self.assertEquals(5, context.exception.pos, 'Not closed quote pos')


if __name__ == '__main__':
    unittest.main()

