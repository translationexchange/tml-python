# encoding: UTF-8
"""
# Language cases: apply case for variable like {user::dat} 
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
__author__ = 'a@toukmanov.ru'

from .contexts import Gender, Value
from . import ContextRules
from argparse import ArgumentError
from .parser import parse


class Case(ContextRules):
    """ Language case """
    def execute(self, value):
        """ Execute case for value """
        data = {'value': Value.match(value)}
        try:
            # Try to detect gender:
            data['gender'] = Gender.match(value)
        except ArgumentError:
            # Undefined gender:
            data['gender'] = Gender.OTHER
        return self.apply(data)

    @classmethod
    def from_rules(cls, rules):
        """ Build case from rules
            Args:
                rules (dict): view API response contexts.*.rules or cases.*.rules
        """
        ret = cls([], ['quote', '@value'])
        for rule in rules:
            ret.choices.append((parse(rule['conditions']),
                                parse(rule['operations'])))
        return ret

    @classmethod
    def from_data(cls, data, safe = False):
        """ Build cases from API response
            Args:
                data (dict): look cases in language API respons
                safe (boolean): handle errror
            Return:
                (dict, dict): list of rules, list of errors
        
        """
        catch = Exception if safe else None
        ret = {}
        errors = {}
        for key in data:
            try:
                ret[key] = cls.from_rules(data[key]['rules'])
            except catch as rule_parse_fault:
                errors[key] = rule_parse_fault
        return (ret, errors)

