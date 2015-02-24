# encoding: UTF-8
from .engine import RulesEngine, Error as EngineError
from .functions import SUPPORTED_FUNCTIONS
from .parser import parse
from tests.unit import rules


default_engine = RulesEngine(SUPPORTED_FUNCTIONS) # default engine

class Case(object):
    """ Case of rules """
    def __init__(self, choices, default, engine = default_engine):
        """ .ctor
            choices ((conditions, operations)[]): list of instructions to engine
            default (list): default engine instruction, will be executed if each condition is False
            engine (RulesEngine): engine to execute insructions
        """
        self.choices = choices
        self.default = default
        self.engine = engine

    def apply(self, data):
        for conditions, operations in self.choices:
            if (self.engine.execute(conditions, data)):
                # if data is under conditions execute operations:
                return self.engine.execute(operations, data)
        # Defalt:
        return self.engine.execute(self.default, data)

    @classmethod
    def from_rules(cls, rules):
        """ Build case from rules
            Args:
                rules (dict): view API response contexts.*.rules or cases.*.rules
        """
        ret = Case([], ['@value'])
        for key in rules:
            rule = rules[key]
            operations = parse(rule['operations']) if 'operations' in rule else ['quote', key] # if operations is not defined - just return a key
            if 'conditions' in rule:
                # has conditions:
                ret.choices.append((parse(rule['conditions']), operations))
            else:
                # no conditions - default:
                ret.default = operations
        return ret

