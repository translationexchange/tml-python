# encoding: UTF-8
# --
# Copyright (c) 2015, Translation Exchange, Inc.
#
#  _______                  _       _   _             ______          _
# |__   __|                | |     | | (_)           |  ____|        | |
#    | |_ __ __ _ _ __  ___| | __ _| |_ _  ___  _ __ | |__  __  _____| |__   __ _ _ __   __ _  ___
#    | | '__/ _` | '_ \/ __| |/ _` | __| |/ _ \| '_ \|  __| \ \/ / __| '_ \ / _` | '_ \ / _` |/ _ \
#    | | | | (_| | | | \__ \ | (_| | |_| | (_) | | | | |____ >  < (__| | | | (_| | | | | (_| |  __/
#    |_|_|  \__,_|_| |_|___/_|\__,_|\__|_|\___/|_| |_|______/_/\_\___|_| |_|\__,_|_| |_|\__, |\___|
#                                                                                        __/ |
#                                                                                       |___/
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
#++
from _ctypes import ArgumentError

__author__ = 'randell'

from datetime import date
from compiler.misc import flatten
import re


class ParseError(Exception):
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
        self.message = message
        self.code = code
        self.text = text
        self.pos = pos

    def __str__(self, *args, **kwargs):
        return 'Expression parse error %s in "%s" at symbol %d' % (self.message, self.text, self.pos)


class Evaluator:
    @staticmethod
    def drop():
        def f(list, n):
            [list.pop(0) for i in (0, n)]
            return list

        return f

    def __init__(self):
        self.vars = {}

        def label():
            def f(l, r):
                self.vars[l] = r
                return r

            return f

        def in_f():
            def f(values, search):
                search = str(search).strip()
                for e in values.split(','):
                    if e.find('..') > 0:
                        bounds = e.strip().split('..')
                        if search in list(range(bounds[0].strip(), bounds[-1].strip())):
                            return True
                        elif (e.strip() == search):
                            return True
                return False

            return f

        def replace():
            def f(search, replace_with, s):
                if re.compile('/\/i$/').match(subject):
                    replace_with = re.compile("/\$(\d+)/").sub(replace_with,
                                                               '\\\\\1')  # for compatibility with Perl notation
                search = self.regexp_from_string(search)
                search.sub(subject, replace)
                return subject

            return f

        def within():
            def f(values, search):
                bounds = map(values.split('..'), lambda d: int(d))
                return search in list(range(bounds[0], bounds[-1]))

        self.env = {  
            # McCarthy's Elementary S-functions and Predicates
            'label': lambda l, r: label()(l, r),
            'quote': lambda expr: expr,
            'car': lambda list: list[1],
            'cdr': lambda list: Evaluator.drop()(list, 1),
            'cons': lambda e, cell: [e] + cell,
            'eq': lambda l, r: l == r,
            'atom': lambda expr: isinstance(expr, (type(None), str, int, float, bool)),
            'cond': lambda c, t, f: (self.evaluate(t) if self.evaluate(c) else self.evaluate(f)),
            # Tr8n Extensions
            '=': lambda l, r: l == r,  # ['=', 1, 2]
            '!=': lambda l, r: l != r,  # ['!=', 1, 2]
            '<': lambda l, r: l < r,  # ['<', 1, 2]
            '>': lambda l, r: l > r,  # ['>', 1, 2]
            '+': lambda l, r: l + r,  # ['+', 1, 2]
            '-': lambda l, r: l - r,  # ['-', 1, 2]
            '*': lambda l, r: l * r,  # ['*', 1, 2]
            '%': lambda l, r: l % r,  # ['%', 14, 10]
            'mod': lambda l, r: l % r,  # ['mod', '@n', 10]
            '/': lambda l, r: (l * 1.0) / r,  # ['/', 1, 2]
            '!': lambda expr: not expr,  # ['!', ['true']]
            'not': lambda val: not val,  # ['not', ['true']]
            '&&': lambda exprs: all(self.evaluate(expr) for expr in exprs),  # ['&&', [], [], ...]
            'and': lambda exprs: all(self.evaluate(expr) for expr in exprs),  # ['and', [], [], ...]
            '::': lambda exprs: any(self.evaluate(expr) for expr in exprs),  # ['::', [], [], ...]
            'or': lambda exprs: any(self.evaluate(expr) for expr in exprs),  # ['or', [], [], ...]
            'if': lambda c, t, f: self.evaluate(t) if self.evaluate(c) else self.evaluate(f),# ['if', 'cond', 'true', 'false']
            'let': lambda l, r: label()(l, r),  # ['let', 'n', 5]
            'true': lambda:True,  # ['true']
            'false': lambda: False,  # ['false']
            'date': lambda date: date.strptime(date, '%Y-%m-%d'),# ['date', '2010-01-01']
            'today': lambda: date.now().today(),  # ['today']
            'time': lambda time: date.strptime(time, '%Y-%m-%d %H:%M:%S'),  # ['time', '2010-01-01 10:10:05']
            'now': lambda: date.now(),  # ['now']
            'append': lambda l, r: str(r) + str(l),  # ['append', 'world', 'hello ']
            'prepend': lambda l, r: str(l) + str(r),  # ['prepend', 'hello  ', 'world']
            'match': lambda search, subject: not self.regexp_from_string(search).match(subject),  # ['match', /a/, 'abc']
            'in': lambda values, search: in_f()(values, search),  # ['in', '1,2,3,5..10,20..24', '@n']
            'within': lambda values, search: within(values, search),  # ['within', '0..3', '@n']
            'replace': lambda search, replace, subject: replace()(search, replace, subject),
            'count': lambda list: len(self.vars[list] if isinstance(list, str) else list),  # ['count', '@genders']
            'all': lambda list, value: all([v == value for v in flatten(list)]),  # ['all', '@genders', 'male']
            'any': lambda list, value: any([v == value for v in flatten(list)])  # ['any', '@genders', 'female']
        }

        def regexp_from_string(self, str):
            pattern = re.compile(str)
            pattern2 = "^\/"
            match1 = re.match(pattern2, str)
            if not match1:
                return pattern
            str = re.compile("/^\//").sub('', str)
            if re.compile("\/i$/").match(str):
                str = re.compile("/\/i$/").sub("", str)
                return re.compile("/%s/i" % str)
            str = re.compile("/\/$/").sub('', str)
            return re.compile("/%s/" % str)


        def reset(self):
            self.vars = {}

        def apply(self, fn, args):
            if (fn not in self.env.keys()):
                raise ArgumentError("undefined symbols #{fn}")
            self.env[fn].call(*args)

        #
        def evaluate(self, expr):
            None
            if self.env['atom'].call(expr):
                return self.vars[expr] if (expr is string and self.vars[expr]) else expr

            fn = expr[0]
            args = Evaluator.drop(expr, 1)

            if fn not in ['quote', 'car', 'cdr', 'cond', 'if', '&&', '||', 'and', 'or', 'true', 'false', 'let', 'count',
                          'all', 'any']:
                args = map(args, lambda a: self.evaluate(a))

            self.apply(fn, args)


