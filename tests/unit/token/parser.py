# encoding: UTF-8
"""
# Copyright (c) 2015, Translation Exchange, Inc.
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from __future__ import absolute_import
from __future__ import print_function
import unittest
from tml.token import VariableToken, TextToken, RulesToken, PipeToken,\
    TokenMatcher, execute_all
from tml.token.parser import TokenParser, IS_TOKEN
from tests.unit.token import FakeLanguage


class ParserTest(unittest.TestCase):
    def test_parse(self):
        p = TokenParser(IS_TOKEN,
                        TokenMatcher([TextToken,
                                      VariableToken,
                                      RulesToken,
                                      PipeToken]))
        tokens = p.parse('{name} give you {count||apple} for free', FakeLanguage())
        self.assertEquals(4, len(tokens), 'Splited to 4 tokens')
        self.assertEquals(VariableToken, tokens[0].__class__, '{name} is varible')
        self.assertEquals(TextToken, tokens[1].__class__, '"give you" is text')
        self.assertEquals(' give you ', tokens[1].execute({}, {}), '" give you " with spaces')
        self.assertEquals(PipeToken, tokens[2].__class__, 'find pipe token')
        self.assertEquals('John give you 1 apple for free', execute_all(tokens, {'name':'John', 'count': 1}, {}))
        self.assertEquals('Hello John',
                          execute_all(p.parse(
                                              'Hello {$0}',
                                              FakeLanguage),
                                      'John',
                                      {}) ,
                          '{$0}')

if __name__=='__main__':
    unittest.main()

