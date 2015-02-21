# encoding: UTF-8
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
        fn_name = rule[0]
        try:
            fn = self.functions[rule[0]]
        except KeyError:
            raise FunctionDoesNotExists(rule, data, 0)
        args = []
        part_number = 0
        for arg in rule[1:]:
            """ Build args """
            part_number = part_number + 1
            if type(arg) is list:
                # inner rule expressions (mod ^(sum @n 5) 10):
                try:
                    args.append(self.execute(arg, data))
                except Error as e:
                    raise InnerExpressionCallFault(e, rule, data, part_number)
            elif arg[0] == '@':
                # une data value (mod ^@n 10):
                try:
                    args.append(data[arg[1:]])
                except KeyError as e:
                    raise ArgumentDoesNotExists(arg, rule, data, part_number)
            else:
                # text arg (mod @n ^10)
                args.append(arg)
        try:
            return fn(*args)
        except Exception as e:
            raise FunctionCallFault(e, rule, data)


class Error(BaseError):
    """ Base error """
    def __init__(self, rule, data, part_number = None):
        """ Rule execution error
            Args:
                rule (list): rule
                data (dict): rule kwargs
                part_number (int): part of rule where error occurs
        """
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

    def __str__(self):
        return 'Function call fault in function %s with %s: %s' % (self.rule[0], self.exception.__class__.__name__, self.exception)

class InnerExpressionCallFault(Error):
    """ Inner error """
    def __init__(self, exception, rule, data, part_number):
        """ Error in inner e
        
        """
        super(InnerExpressionCallFault, self).__init__(rule, data, part_number)
        self.exception = exception

    @property
    def parent_error(self):
        return self.exception

