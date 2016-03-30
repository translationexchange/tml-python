# encoding: UTF-8
"""
# Date variable
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
import six
__author__ = 'a@toukmanov.ru'


from _ctypes import ArgumentError
from datetime import date, datetime
import six


class Date(date):
    """ Date context """
    key = 'date'
    supported_formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']

    @classmethod
    def match(cls, data):
        """ Check is data has a date context
            Args:
                data (mixed): data
            Throws:
                ArgumentException
            Returns:
                date
        """
        if isinstance(data, datetime):
            return data.date()
        elif isinstance(data, date):
            return data
        elif isinstance(data, six.string_types) or type(data) is six.text_type:
            for date_format in cls.supported_formats:
                try:
                    return datetime.strptime(data, date_format).date()
                except ValueError :
                    pass
        raise NotDate(data)

class NotDate(ArgumentError):
    """ Argument is not a date """
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return 'Given data is not date: "%s"' % self.data

