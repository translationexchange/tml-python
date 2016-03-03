# encoding: UTF-8
"""
# Rules engine: execute rule
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
__author__ = ''

from ..exceptions import Error as BaseError

class RulesEngine(object):
    """ Rules execution engine """
    def __init__(self, functions):
        """ .ctor
            Args:
                functions (dict{function}): supported functions
        """
        self.functions = functions


    def execute(self, rule, data):
        """ Execute rule
            Args:
                rule (list): rule [fn_name, arg1, arg2, ...]
                data (dict): rule arguments kwargs
        """
        # Fetch functions:
        try:
            func = self.functions[rule[0]]
        except KeyError:
            raise FunctionDoesNotExists(rule, data, 0)
        args = []
        part_number = 0
        for arg in rule[1:]:
            # Build args:
            part_number = part_number + 1
            if type(arg) is list:
                # inner rule expressions (mod ^(sum @n 5) 10):
                try:
                    args.append(self.execute(arg, data))
                except Error as error:
                    raise InnerExpressionCallFault(error,
                                                   rule,
                                                   data,
                                                   part_number)
            elif arg[0] == '@':
                # une data value (mod ^@n 10):
                try:
                    args.append(data[arg[1:]])
                except KeyError:
                    raise ArgumentDoesNotExists(arg, rule, data, part_number)
            else:
                # text arg (mod @n ^10)
                args.append(arg)
        try:
            return func(*args)
        except Exception as func_error:
            raise FunctionCallFault(func_error, rule, data)


class Error(BaseError):
    """ Base error """
    def __init__(self, rule, data, part_number = None):
        """ Rule execution error
            Args:
                rule (list): rule
                data (dict): rule kwargs
                part_number (int): part of rule where error occurs
        """
        super(Error, self).__init__()
        self.rule = rule
        self.data = data
        self.part_number = part_number

    @property
    def parent_error(self):
        """ Parent error:
            Returns:
                Exception
        """
        return self


class FunctionDoesNotExists(Error):
    """ Call of not exists function """
    def __str__(self, *args, **kwargs):
        return 'Function %s does not exists' % (self.rule[0])

class ArgumentDoesNotExists(Error):
    """ Function argument is not passed """
    def __init__(self, argment_name, rule, data, part_number = None):
        self.argument_name = argment_name
        super(ArgumentDoesNotExists, self).__init__(rule, data, part_number)

    def __str__(self, *args, **kwargs):
        return 'Argument %s does not exists' % self.argument_name

class FunctionCallFault(Error):
    """ Function fault with exceptions """
    def __init__(self, exception, rule, data):
        super(FunctionCallFault, self).__init__(rule, data)
        self.exception = exception

    MESSAGE = 'Function call fault in %s with %s: %s'

    def __str__(self):
        return self.MESSAGE % (', '.join(self.rule),
                               self.exception.__class__.__name__,
                               self.exception)

class InnerExpressionCallFault(Error):
    """ Inner error """
    def __init__(self, exception, rule, data, part_number):
        """ Error in inner e

        """
        super(InnerExpressionCallFault, self).__init__(rule, data, part_number)
        self.exception = exception

    def __str__(self):
        return str(self.exception)

    @property
    def parent_error(self):
        return self.exception

