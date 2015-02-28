# encoding: UTF-8
""" Test rules built-in functions """
import unittest
from tml.rules.contexts import *


def die(object):
    raise Exception('Bad function')


class Dumn(object):
    def __str__(self):
        return 'qwerty'


class rules_variables(unittest.TestCase):
    """ Test for rules variables """
    def setUp(self):
        number_options = ['one','few','many','other']
        number_default_option = 'many'
        number_token_mapping = [TokenMapping.UNSUPPORTED,
                                TokenMapping.UNSUPPORTED,
                                {'one':'{$0}', 'few':'{$1}', 'many':'{$2}','other':'{$2}'},
                                {'one':'{$0}', 'few':'{$1}', 'many':'{$2}','other':'{$3}'}]
        number_rules = {'one':{'conditions':'(&& (= 1 (mod @n 10)) (!= 11 (mod @n 100)))'},
                        'few':{'conditions':'(&& (in \'2..4\' (mod @n 10)) (not (in \'12..14\' (mod @n 100))))'},
                        'many':{'conditions':'(|| (= 0 (mod @n 10)) (in \'5..9\' (mod @n 10)) (in \'11..14\' (mod @n 100)))'}}
        number_default_rule = 'other'
        number_variable_name = 'n'
        self.number = Context(Number,
                              OptionsParser(number_options,
                                            number_default_option,
                                            TokenMapping.build(number_token_mapping)),
                                            RulesCase.from_rules(number_rules, number_default_rule),
                              number_variable_name)
        gender_options = ['male','female','other']
        gender_default_option = 'other'
        gender_token_mapping = [{'other':'{$0}'},
                                {'male':'{$0}','female':'{$1}','other':'{$0}/{$1}'},
                                {'male':'{$0}','female':'{$1}','other':'{$2}'}]
        gender_rules = {'male':{'conditions':'(= \'male\' @gender)'},
                        'female':{'conditions':'(= \'female\' @gender)'},
                        'other':{}}
        gender_default_rule = 'other'
        gender_variable_name = 'gender'
        self.gender = Context(Gender,
                      OptionsParser(gender_options,
                                    gender_default_option,
                                    TokenMapping.build(gender_token_mapping)),
                                    RulesCase.from_rules(gender_rules, gender_default_rule),
                      gender_variable_name)
        self.api_response = {'number':{'default_key': number_default_option,
                                       'keys': number_options,
                                       'rules': number_rules,
                                       'token_mapping': number_token_mapping,
                                       'variables':['@%s'%number_variable_name]},
                             'gender':{'default_key': gender_default_option,
                                       'keys': gender_options,
                                       'rules': gender_rules,
                                       'token_mapping': gender_token_mapping,
                                       'variables':['@%s' % gender_variable_name]},
                             'something_unsupported':'Ignore me anyway'}


    def test_context(self):
        self.assertEquals('one', self.number.option(21), 'Check option')
        self.assertEquals('few', self.number.option(32), 'Check option')
        self.assertEquals('many', self.number.option(40), 'Check option')
        self.assertEquals('тест', self.number.execute('тест, теста, тестов', 1), '1 тест')
        self.assertEquals('тестов', self.number.execute('тест, теста, тестов', 11), '11 тестов')
        self.assertEquals('теста', self.number.execute('тест, теста, тестов', 2), '2 теста')
        with self.assertRaises(ValueIsNotMatchContext) as context:
            self.number.execute('тест, теста, тестов', 'AAA')
        self.assertEquals('AAA', context.exception.value, 'Store value')
        self.assertEquals('пошел', self.gender.execute('пошел, пошла', 'male'))

    def test_contexts(self):
        contexts = Contexts([self.gender, self.number])
        self.assertEquals('тест', contexts.execute('тест, теста, тестов', 1), '1 тест')
        self.assertEquals('пошел', contexts.execute('пошел, пошла', 'male'))
        self.assertEquals('яблока', contexts.execute('one: яблоко, few: яблока, many: яблок', 22),'Check last option')

    def test_fetcher(self):
        contexts = Contexts.from_dict(self.api_response)
        self.assertEquals(2, len(contexts.contexts), 'Only gender and number')
        number = contexts.find_by_code('number')
        self.assertEquals(Number, number.pattern, 'Check context search')
        self.assertEqual('n', number.variable_name, 'Check variable name')
        with self.assertRaises(ContextNotFound):
            contexts.find_by_code(':(')
        # check order:
        self.assertEqual(contexts.contexts[0].pattern, Gender, 'Check contexts order')


if __name__ == '__main__':
    unittest.main()

