# -*- coding: utf-8 -*-
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

class Error(Exception):
    """ Base TML exception """
    pass


class RequiredArgumentIsNotPassed(Error):
    """ Throw if required argument is not passed to render function """
    def __init__(self, key, data):
        self.key = key
        self.data = data
        super(RequiredArgumentIsNotPassed, self).__init__()


class MethodDoesNotExist(Error):
    def __init__(self, var_name, meth_name):
        self.var_name = var_name
        self.method_name = meth_name

    def __str__(self):
        return "Variable `%s` has no method called `%s`" % (self.var_name, self.method_name)
