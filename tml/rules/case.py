from contexts import Gender, Value
from . import ContextRules, default_engine
from argparse import ArgumentError
from .parser import parse


class Case(ContextRules):
    """ Language case """
    def execute(self, value):
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
            ret.choices.append((parse(rule['conditions']), parse(rule['operations'])))
        return ret

