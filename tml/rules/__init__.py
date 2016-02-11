# encoding: UTF-8
"""
# Translation rules
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

from .engine import RulesEngine, Error as EngineError
from .functions import SUPPORTED_FUNCTIONS
from .parser import parse


DEFAULT_ENGINE = RulesEngine(SUPPORTED_FUNCTIONS) # default engine


class ContextRules(object):
    """ Case of rules """
    def __init__(self, choices, default, engine = None):
        """ .ctor
            choices ((conditions, operations)[]): list of instructions to engine
            default (list): default engine instruction, will be executed if each condition is False
            engine (RulesEngine): engine to execute insructions
        """
        self.choices = choices
        self.default = default
        self.engine = engine if engine else DEFAULT_ENGINE

    def apply(self, data):
        """ Apply rule for data """
        for conditions, operations in self.choices:
            if (self.engine.execute(conditions, data)):
                # if data is under conditions execute operations:
                return self.engine.execute(operations, data)
        # Defalt:
        return self.engine.execute(self.default, data)

    @classmethod
    def from_rules(cls, rules, default = None):
        """ Build case from rules
            Args:
                rules (dict): view API response contexts.*.rules or cases.*.rules
        """
        ret = cls([], ['quote', default])
        for key in rules:
            rule = rules[key]
            operation = '(quote %s)' % key
            if 'conditions' in rule:
                # has conditions:
                ret._append(rules[key]['conditions'], operation)
            else:
                # no conditions - default:
                ret.default = parse(operation)
        return ret

    def _append(self, condition, operation):
        self.choices.append((parse(condition), parse(operation)))

