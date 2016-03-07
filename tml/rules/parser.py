# encoding: UTF-8
"""
# Rules parser
#
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
__author__ = ''

import re
from ..exceptions import Error

NO_EXPRESSION_PATTERN = re.compile('^\@(\w+)$')
NO_EXPRESSION = '(quote @%s)'

QUOTES = ['"',"'"]


def parse(text):
    """ Parse rule
        Args:
            rule (string): string
        Returns:
            list: list of notations
    """
    pos = 0 # current symbol position
    expression = [] # current expression
    argument = None # current argument
    quote = None
    stack = [] # expressions stack
    stack_pos = []
    # @value:
    just_return = NO_EXPRESSION_PATTERN.match(text)
    if just_return:
        return parse(NO_EXPRESSION % just_return.group(1))
    # Check that expression is in brackets:
    if text[0] != '(':
        raise ParseError('No opened bracked found',
                         ParseError.INVALID_SYNTAX,
                         text,
                         0)
    if text[-1] != ')':
        raise ParseError('No closed bracked found',
                         ParseError.INVALID_SYNTAX,
                         text,
                         len(text)-1)

    def flush(expression, argument):
        """ Flush argument to expression
            Args:
                expression (list): expression
                argument (list|None): appended argument
            Returns:
                tuple(expression, argument)
        """
        if argument:
            expression.append(''.join(argument))
        return (expression, None)

    for let in text[1:-1]:
        pos = pos + 1 # calculate symbol
        if let in QUOTES:
            # Quotation like ("Some quoted text")
            if quote is None:
                # Start new argument:
                # (upper ^"Any data inside")
                if not argument is None:
                    # Unexpected quotation inside argument:
                    # (print like^"to mix quotes")
                    raise ParseError('Unexpected quote',
                                     ParseError.INVALID_SYNTAX,
                                     text,
                                     pos)
                argument = []
                quote = pos
                quote_type = let
            elif quote_type == let:
                # Close argument:
                # (upper "Any data inside^")
                expression, argument = flush(expression, argument)
                quote = None
                quote_type = None
            else:
                # inner quote:
                argument.append(let)
        elif not quote is None:
            # We are inside quoted argument:
            # ignore any special symbol and just push to argument
            # like (upper "Any^ data inside")
            argument.append(let)
        else:
            if let == '(':
                # begin next expression: (sum ^(mod 25 10) 2):
                expression, argument = flush(expression, argument)
                stack.append(expression) # store current expression in stack
                stack_pos.append(pos)
                expression = [] # create empty expression
            elif let == ')':
                # end of embed expression: (sum (mod 25 10^) 2):
                if len(stack) == 0:
                    # No expression to pop:
                    raise ParseError('Unexpected )',
                                     ParseError.UNEXPECTED_EXPRESSION_FINISH,
                                     text,
                                     pos)
                inner_expression, argument = flush(expression, argument)
                expression = stack.pop() # pop expression from stack
                stack_pos.pop() # forgot about last pos
                expression.append(inner_expression)
            elif let == ' ':
                # Next argument:
                if not argument is None:
                    # check argument for double space bug: (arg1  arg2)
                    expression, argument = flush(expression, argument)
            elif argument:
                # Append data to argument:
                argument.append(let)
            else:
                # Begin new argument:
                argument = [let]
    # OK, finished:
    if quote:
        # Quotation is not closed:
        raise ParseError('Quotation is not closed',
                         ParseError.QUOTE_IS_NOT_CLOSED,
                         text,
                         quote)
    if len(stack_pos):
        raise ParseError('Expression is not closed',
                         ParseError.EXPRESSION_IS_NOT_CLOSED,
                         text,
                         stack_pos.pop())
    # Flush last argument:
    expression, argument = flush(expression, argument)
    if len(expression) == 0:
        raise ParseError('Expression is empty',
                         ParseError.EMPTY_EXPRESSION,
                         text,
                         0)
    return expression


class ParseError(Error):
    """ Parse error """
    INVALID_SYNTAX = 1
    UNEXPECTED_EXPRESSION_FINISH = 2
    QUOTE_IS_NOT_CLOSED = 3
    EXPRESSION_IS_NOT_CLOSED = 4
    EMPTY_EXPRESSION = 5
    def __init__(self, message, code, text, pos = 0):
        """ Expression parsion fault:
            message (string): error message
            code (int): error code
            text (string): parsed expression text
            pos (pos): position in text where error occurs
        """
        super(ParseError, self).__init__()
        self.message = message
        self.code = code
        self.text = text
        self.pos = pos

    MESSAGE = 'Expression parse error %s in "%s" at symbol %d'
    def __str__(self, *args, **kwargs):
        return self.MESSAGE % (self.message, self.text, self.pos)


