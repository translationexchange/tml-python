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
import re
from tml.token import TokenMatcher, data_matcher

class TokenParser(object):
    """ Text parser """
    def __init__(self, regexp, supported_tokens):
        """ Token parser
            Args:
                regexp (_sre.SRE_Pattern): token regext
                supported_tokens (TokenMatcher): token matcher
        """
        self.regexp = regexp
        self.supported_tokens = supported_tokens

    def parse(self, text, language):
        return [self.supported_tokens.build_token(part, language) for part in self.regexp.split(text) if len(part)]



IS_TOKEN = re.compile('(\{.*?\})')
default_parser = TokenParser(IS_TOKEN, data_matcher)

