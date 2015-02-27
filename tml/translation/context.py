# encoding: UTF-8
from tml.rules.contexts import ContextNotFound


class Context(object):
    """ Tranlation context: rules to check is translation good for data """
    def __init__(self, rules):
        """ .ctor
            Args:
                rules (dict): list of rules key - variable name, value - expected
        """
        self.rules = rules


    def check(self, data, options, language):
        """ Check is data supported by context
            Args:
                data (dict): input data
                options (dict): tranlation options
                language (Language): language
            Returns:
                boolean
        """
        for key in self.rules:
            # check any rule:
            for type_code in self.rules[key]:
                expected = self.rules[key][type_code]
                actual = language.contexts.find_by_code(type_code).option(data[key])
                if expected != actual:
                    # Variable is not supported by context
                    return False
        return True

