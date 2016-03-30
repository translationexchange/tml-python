# encoding: UTF-8
"""
# Gender variable
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
from _ctypes import ArgumentError
from tml.strings import to_string

__author__ = 'a@toukmanov.ru'


class Gender(object):
    """ Gender data """
    key = 'gender'
    GENDERS = MALE, FEMALE, OTHER = ('male', 'female', 'other')

    def __init__(self, gender, value):
        self.value = value
        self.gender = Gender.supported_gender(gender)

    @classmethod
    def male(cls, value):
        """ Male factory
            Args:
                value (string): wrapped value
            Returns:
                Gender
        """
        return cls(Gender.MALE, value)

    @classmethod
    def female(cls, value):
        """ Female factory
            Args:
                value (string): wrapped value
            Returns:
                Gender
        """
        return cls(Gender.FEMALE, value)

    @classmethod
    def other(cls, value):
        """ Other factory
            Args:
                value (string): wrapped value
            Returns:
                Gender
        """
        return cls(Gender.OTHER, value)

    def __unicode__(self):
        return to_string(self.value)

    @classmethod
    def supported_gender(cls, gender):
        """ Check is gender string is valid gender """
        if gender in Gender.GENDERS:
            return gender
        raise ArgumentError('Gender unsupported: %s' % gender)

    @classmethod
    def match(cls, data):
        """ Check is object string is valid gender """
        try:
            if isinstance(data, six.string_types):
                # String:
                return Gender.supported_gender(data)
            if (isinstance(data, Gender)):
                # Object is Gender instance:
                gender = data.gender
            elif (isinstance(data, dict)):
                # {'gender':'male'}
                gender = data['gender']
            elif (isinstance(data, object)):
                # check gender property:
                gender = data.gender
        except Exception as e:
            raise ArgumentError('Fault to detect gender for %s' % object, e)
        if not gender:
            raise ArgumentError('No gender at %s' % type(gender))
        return Gender.supported_gender(gender)


