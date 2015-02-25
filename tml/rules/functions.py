# encoding: UTF-8
""" Rules functions """
import re
from _ctypes import ArgumentError
from datetime import date, datetime
import re


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
        min = int(m.group(1))
        max = int(m.group(2))
        if not max > min:
            raise ArgumentError('Invalid range string: max value (%d) seems to be grater than min (%d)' % (max, min), min, max)
        return (min, max)
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
    (min, max) = to_range(range)
    value = to_int(value)
    return value >= min and value <= max


def in_f(set, find):
    """ Check is value in set
        Args:
            find (string): string to find
            set (string): comma separated list of value of ranges 1,2,8..10
        Throws:
            ArgumentError
        Returns:
            boolean
    """
    find = str(find).strip()
    for e in set.split(','):
        e = e.strip()
        if find == e:
            # find == set element
            return True
        elif IS_RANGE.match(e):
            # set element is range:
            if within_f(value = find, range = e):
                return True
    return False

def f_and(*args):
    """ Arg1 AND arg2 ..."""
    return reduce(lambda a, b: bool(a) and bool(b), list)

def f_or(*args):
    """ Arg1 or arg2 ... """
    reduce(lambda a, b: bool(a) or bool(b), list)

IS_PCRE = re.compile('^\/(.*)\/(\w*)$')

def build_flags(flags):
    """ Build python regular expression flags from PCRE flags
        Args:
            flags (string): regulare expression flags : ailms
        Returns:
            int:
    """
    ret = 0
    flags = flags.upper()
    for flag in ('A','I','L','M','S'):
        if flag in flags:
            ret |= getattr(re, flag)
    return ret

def build_regexp(pattern):
    """ Build regexp:
            pattern (string): pattern as python regular expression in PCRE (/pattern/flags)
        Returns:
            _sre.SRE_Pattern
    """
    pcre = IS_PCRE.match(pattern)
    if pcre:
        return re.compile(pcre.group(1), build_flags(pcre.group(2)))
    return re.compile(pattern)


SUPPORTED_FUNCTIONS = {
    # McCarthy's Elementary S-functions and Predicates
    'quote': lambda expr: expr,
    'car': lambda list: list[1],
    'cons': lambda e, cell: [e] + cell,
    'eq': lambda l, r: l == r,
    'atom': lambda expr: isinstance(expr, (type(None), str, int, float, bool)),
    # Tr8n Extensions
    '=': lambda l, r: l == r,  # ['=', 1, 2]
    '!=': lambda l, r: l != r,  # ['!=', 1, 2]
    '<': lambda l, r: float(l) < float(r),  # ['<', 1, 2]
    '>': lambda l, r: float(l) > float(r),  # ['>', 1, 2]
    '+': lambda l, r: l + r,  # ['+', 1, 2]
    '-': lambda l, r: l - r,  # ['-', 1, 2]
    '*': lambda l, r: l * r,  # ['*', 1, 2]
    '%': lambda l, r: l % r,  # ['%', 14, 10]
    'mod': lambda l, r: l % r,  # ['mod', '@n', 10]
    '/': lambda l, r: (l * 1.0) / r,  # ['/', 1, 2]
    '!': lambda expr: not expr,  # ['!', ['true']]
    'not': lambda val: not val,  # ['not', ['true']]
    '&&': lambda a, b: a and b,  # ['&&', [], [], ...]
    'and': all,  # ['and', [], [], ...]
    '::':any,  # ['::', [], [], ...]
    'or': any,  # ['or', [], [], ...]
    'if': lambda c, t, f: t if c else f,# ['if', 'cond', 'true', 'false']
    'true': lambda: True,  # ['true']
    'false': lambda: False,  # ['false']
    'date': lambda date: date.strptime(date, '%Y-%m-%d'),# ['date', '2010-01-01']
    'today': lambda: date.now().today(),  # ['today']
    'time': lambda time: date.strptime(time, '%Y-%m-%d %H:%M:%S'),  # ['time', '2010-01-01 10:10:05']
    'now': lambda: date.now(),  # ['now']
    'append': lambda l, r: str(r) + str(l),  # ['append', 'world', 'hello ']
    'prepend': lambda l, r: str(l) + str(r),  # ['prepend', 'hello  ', 'world']
    'match': lambda pattern, string, flags = None: re.match(build_regexp(pattern), string, flags),  # ['match', /a/, 'abc']
    'in': in_f,  # ['in', '1,2,3,5..10,20..24', '@n']
    'within': within_f,  # ['within', '0..3', '@n']
    'replace': lambda search, replace, subject: replace()(search, replace, subject),
    'count': len,  # ['count', '@genders']
    'all': lambda of, value: all([el == value for el in of]),  # ['all', '@genders', 'male']
    'any': lambda of, value: any([el == value for el in of])  # ['any', '@genders', 'female']
}
