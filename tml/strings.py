# encoding: UTF-8
"""
# Copyright (c) 2015, Translation Exchange, Inc.
#
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

def to_string(text):
    """ Safe string conversion 
        Args:
            text (string|unicode): input string
        Returns:
            str
    """
    if type(text) is six.text_type:
        return text
    if hasattr(text, '__html__'):
        return six.text_type(text.__html__())
    if hasattr(text, '__unicode__'):
        return text.__unicode__()
    if six.PY3:
        return six.text_type(text)
    else:
        return six.text_type(str(text).decode('utf-8'))


SUGGEST_STRING_KEYS = ['title', 'name', 'html', 'text']

def suggest_string(data):
    """ Suggest string representation for dictionary
        Args:
            data (dict): user data
        Returns:
            string
    """
    if type(data) is dict:
        for key in SUGGEST_STRING_KEYS:
            if key in data:
                return data[key]
        for key in data:
            # Return first key:
            return dict[key]
    return data

