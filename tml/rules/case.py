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
            except catch as e:
                errors[key] = e
        return (ret, errors)
