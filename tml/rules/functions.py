# encoding: UTF-8
""" Rules functions """
import re
from _ctypes import ArgumentError


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

