# encoding: UTF-8
"""
# Functions for rules engine
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
from _ctypes import ArgumentError
from datetime import date
from tml.strings import to_string


INT_REGEXP = '(0|[1-9]\d*)'
IS_INT = re.compile('^%s$' % INT_REGEXP)
IS_RANGE = re.compile('^%s\.\.%s$' % (INT_REGEXP, INT_REGEXP))

def to_int(text):
    """ Convert text to int
        Args:
            text (string): number in string format
        Throws:
            ArgumentError: text has unsupported format
        Returns:
            int
    """
    m = IS_INT.match(str(text).strip())
    if m:
        return int(m.group(1))
    raise ArgumentError('Invalid number string: "%s"' % text)


class InvalidRange(ArgumentError):
    """ Range error """
    def __init__(self, min_value, max_value):
        self.min = min_value
        self.max = max_value

    MESSAGE = 'Invalid range: max (%d) seems to be grater than min (%d)'
    def __str__(self, *args, **kwargs):
        return self.MESSAGE % (self.max, self.min)

def to_range(text):
    """ Convert text to range tuple
        Args:
            text (string): min..max
        Throws:
            ArgumentError: text has unsupported format
        Returns:
            (int, int): (min, max)
    """
    m = IS_RANGE.match(str(text).strip())
    if m:
        min_value = int(m.group(1))
        max_value = int(m.group(2))
        if max_value < min_value:
            raise InvalidRange(min_value, max_value)
        return (min_value, max_value)
    raise ArgumentError('Invalid range string %s' % text)



def within_f(value, range):
    """ Check is value in range
        Args:
            value (string):
            text: range
        Throws:
            ArgumentError
        Returns:
            boolean
    """
    (min_value, max_value) = to_range(range)
    value = to_int(value)
    return min_value <= value <= max_value


def in_f(set, find):
    """ Check is value in set
        Args:
            set (string): comma separated list of value of ranges 1,2,8..10
            find (string): string to find
        Throws:
            ArgumentError
        Returns:
            boolean
    """
    find = to_string(find).strip()
    for e in set.split(','):
        e = to_string(e.strip())
        if to_string(find) == to_string(e):
            # find == set element
            return True
        elif IS_RANGE.match(e):
            # set element is range:
            if within_f(value = find, range = e):
                return True
    return False


IS_PCRE = re.compile('^\/(.*)\/(\w*)$')

def build_flags(flags):
    """ Build python regular expression flags from PCRE flags
        Args:
            flags (string): regulare expression flags : ailms
        Returns:
            int:
    """
    U = set(('A', 'I', 'L', 'M', 'S'))
    ret = 0
    if flags is None:
        return ret
    flags = flags.upper()
    for flag in set(flags) & U:
        ret |= getattr(re, flag)
    return ret

def build_regexp(pattern, flags = None):
    """ Build regexp:
            pattern (string): pattern as python regular expression in PCRE (/pattern/flags)
        Returns:
            _sre.SRE_Pattern
    """
    flags = build_flags(flags)
    pattern = to_string(pattern)
    pcre = IS_PCRE.match(pattern)
    if pcre:
        pattern = pcre.group(1)
        flags = flags | build_flags(pcre.group(2))
    return re.compile(pattern, flags)

def f_mod(l, r):
    return int(l) % int(r)

def f_any(*args):
    return any(args)

def f_all(*args):
    return all(args)

def f_eq(*args):
    if any([type(arg) is int for arg in args]):
        # convert all arguments to int if int argumnt exists
        try:
            args = [int(arg) for arg in args]
        except ValueError:
            # can not convert argument to int <-> !=
            return False
    return all([args[0] == arg for arg in args])

def cmp_args(arg1, arg2):
    if type(arg1) is date and type(arg2) is date:
        pass
    else:
        arg1 = float(arg1)
        arg2 = float(arg2)
    if arg1 == arg2:
        return '='
    elif arg1 > arg2:
        return '>'
    else:
        return '<'


def f_match (pattern, string, flags = None):
    """ Match function
        Args:
            pattern (string): regexp (pattern|/pattern/flags)
            string (string): tested string
            flags (int): regexp flage
        Return:
            boolean
    """
    if build_regexp(pattern, flags).search(to_string(string)):
        return True
    return False

def f_replace(search, replace, subject):
    """ Match function
        Args:
            search (string): search regexp (pattern|/pattern/flags)
            replace (string): replacement
            subject (string): text to replace
        Return:
            boolean
    """
    ret = build_regexp(search).sub(
                             replace,
                             subject)
    return to_string(ret)


SUPPORTED_FUNCTIONS = {
    # McCarthy's Elementary S-functions and Predicates
    'quote': lambda expr: expr,
    'car': lambda lst: lst[0],
    'cdr': lambda lst: lst[1:],
    'cons': lambda e, cell: [e] + cell,
    'eq': lambda l, r: l == r,
    'atom': lambda expr: isinstance(expr, (type(None), str, int, float, bool)),
    # Tr8n Extensions
    '=': f_eq,  # ['=', 1, 2]
    '!=': lambda l, r: '=' != cmp_args(l, r),  # ['!=', 1, 2]
    '<': lambda l, r: '<' == cmp_args(l, r),  # ['<', 1, 2]
    '>': lambda l, r: '>' == cmp_args(l, r),  # ['>', 1, 2]
    '+': lambda l, r: float(l) + float(r),  # ['+', 1, 2]
    '-': lambda l, r: float(l) - float(r),  # ['-', 1, 2]
    '*': lambda l, r: float(l) * float(r),  # ['*', 1, 2]
    '%': f_mod,  # ['%', 14, 10]
    'mod': f_mod,  # ['mod', '@n', 10]
    '/': lambda l, r: (l * 1.0) / r,  # ['/', 1, 2]
    '!': lambda expr: not expr,  # ['!', ['true']]
    'not': lambda val: not val,  # ['not', ['true']]
    '&&': f_all,  # ['&&', [], [], ...]
    'and': f_all,  # ['and', [], [], ...]
    '::': f_any,  # ['::', [], [], ...]
    '||': f_any,
    'or': f_any,  # ['or', [], [], ...]
    'if': lambda c, t, f: t if c else f,# ['if', 'cond', 'true', 'false']
    'true': lambda: True,  # ['true']
    'false': lambda: False,  # ['false']
    'date': lambda date: date.strptime(date, '%Y-%m-%d'),# ['date', '2010-01-01']
    'today': lambda: date.today(),  # ['today']
    'time': lambda time: date.strptime(time, '%Y-%m-%d %H:%M:%S'),  # ['time', '2010-01-01 10:10:05']
    'now': lambda: date.now(),  # ['now']
    'append': lambda l, r: to_string(r) + to_string(l),  # ['append', 'world', 'hello ']
    'prepend': lambda l, r: to_string(l) + to_string(r),  # ['prepend', 'hello  ', 'world']
    'match': f_match, # ['match', /a/, 'abc']
    'in': in_f,  # ['in', '1,2,3,5..10,20..24', '@n']
    'within': within_f,  # ['within', '0..3', '@n']
    'replace': f_replace,
    'count': len,  # ['count', '@genders']
    'all': lambda of, value: all([el == value for el in of]),  # ['all', '@genders', 'male']
    'any': lambda of, value: any([el == value for el in of])  # ['any', '@genders', 'female']
}

