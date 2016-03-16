# encoding: UTF-8
""" Test rules built-in functions """
from __future__ import absolute_import
import unittest
import pytest
from tests.mock import Client as ClientMock
from tml.rules.options import *


@pytest.mark.usefixtures("build_context")
class OptionsTest(unittest.TestCase):
    """ Test for options """

    def setUp(self):
        self.client = ClientMock.read_all()

    def test_parse_args(self):
        """ Test parser """
        self.assertEquals((['a', 'b'],{}), parse_args('a, b'), 'a,b')
        self.assertEquals((['a', 'b'],{}), parse_args(' a,b '), ' a,b ')
        self.assertEquals(([],{'one':'1', 'two':'2'}), parse_args('one: 1, two: 2'), 'one: 1, two: 2')
        self.assertEquals(([],{'one':'1', 'two':'2'}), parse_args(' one : 1, two : 2 '), 'more spaces: " one : 1, two : 2 "')
        self.assertEquals((['a', 'b'],{'one':'1', 'two':'2'}), parse_args('a, one : 1, two : 2, b '), 'a, one : 1, two : 2, b ')

    def test_token_mapping(self):
        self.assertEquals({'one':'one','few':'few','many':'many','other':'many'},
                          TokenMapping({"one":"{$0}","few":"{$1}","many":"{$2}","other":"{$2}"}).
                          apply(['one','few','many']),
                          )
        self.assertEquals({'male':'he','female':'she','other':'he or she'},
                          TokenMapping({"male":"{$0}","female":"{$1}","other":"{$0} or {$1}"}).
                          apply(['he','she']),
                          'He, she + template for other')
        m = self._build_mapping()
        self.assertEquals([1,2], list(m.keys()), 'Map 2 keys')


    def _build_mapping(self):
        return TokenMapping.build(['unsupported',
                            {"male":"{$0}","female":"{$1}","other":"{$0} or {$1}"},
                            {"male":"{$0}","female":"{$1}","other":"{$2}"}])

    def test_parser(self):
        """ Test parser """
        p = Parser(['male','female','other'], 'other', self._build_mapping())
        self.assertEquals({'male':'he','female':'she','other':'it'},
                          p.parse('male: he, female: she, other: it'),
                          'Parse: "male: he, female: she, other: it"')

        self.assertEquals({'male':'he','female':'she','other':'he or she'},
                          p.parse('he, she'),
                          'Parse: "he, she"')

        self.assertEquals({'male':'he','female':'she','other':'it'},
                          p.parse('he, she, it'),
                          'Parse: "he, she, it"')

        self.assertEquals({'male':'somebody','female':'she','other':'somebody'},
                          p.parse('female: she, other: somebody'),
                          'Apply defaults: "female: she, other: somebody"')

        with self.assertRaises(InvalidNumberOfArguments):
            p.parse('he')

        with self.assertRaises(InvalidNumberOfArguments):
            p.parse('he,she,it,somebody')

        with self.assertRaises(MixOfNamedAndOrderedArgs):
            p.parse('male: he, she, it')

        with self.assertRaises(UnsupportedKey):
            p.parse('male: he, one: two')

        with self.assertRaises(MissedKey):
            p.parse('male: he, female: she')

    # def test_parser_with_cases(self):
    #     c = self.build_context(client=self.client)
    #     token_mapping = TokenMapping.build([
    #         {"one": "{$0}", "other": "{$0::plural}"},
    #         {"one": "{$0}", "other": "{$1}"}])
    #     p = Parser(['one', 'other'], 'other', token_mapping)
    #     self.assertEquals({'one': 'message', 'other': 'messages'},
    #                       p.parse('one: message, other: messages'))
    #     self.assertEquals({'one': 'message', 'other': 'messages'},
    #                       p.parse('message'))
    #     token_mapping = TokenMapping.build([{"one": "{$0}", "other": "{$10}"}])
    #     p = Parser(['one', 'other'], 'other', token_mapping)
    #     with self.assertRaises(IndexOutOfBounds):
    #         p.parse('message')

    #     token_mapping = TokenMapping.build([{"one": "{$0}", "other": "{$0::bad}"}])
    #     p = Parser(['one', 'other'], 'other', token_mapping)
    #     self.assertEquals({'one': 'message', 'other': 'message'}, p.parse('message'), 'dummy case if case does not exist')

if __name__ == '__main__':
    unittest.main()
