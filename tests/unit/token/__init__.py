# encoding: UTF-8
import unittest
from tml.token import VariableToken, TextToken, RulesToken, PipeToken,\
    TokenMatcher, InvalidTokenSyntax, CaseToken
from tml.rules.contexts.gender import Gender

class FakeLanguage(object):
    def __init__(self):
        self.contexts = self
        self.cases = {'upper': CaseMock()}

    def execute(self, rule, value):
        return rule

class ContextsMock(object):
    """ Stupid class to test context matching """
    @property
    def contexts(self):
        return self

    def execute(self, rules, data):
        return data.__class__.__name__

class CaseMock(object):
    def execute(self, data):
        return data.upper()


class TokenTest(unittest.TestCase):
    def setUp(self):
        self.language = FakeLanguage()

    """ Test client """
    def text_parse_text(self):
        """ Parse text """
        t = TextToken.validate('test', self.language)
        self.assertEqual(t.__class__, TextToken, 'Fetch text token')
        self.assertEqual('test', t.execute({}, {}), 'Store text')
        # Empty:
        t = TextToken.validate('', self.language)
        self.assertEqual(t.__class__, TextToken, 'Fetch empty token')
        self.assertEqual('', t.execute({}, {}), 'Store text')


    def test_execute_variable(self):
        v = VariableToken('name')
        self.assertEquals('John', v.execute({'name':'John'}, {}), 'Fetch name')
        class Hello(object):
            def __str__(self, *args, **kwargs):
                return 'Hello'
        self.assertEquals(u'Hello', 
                          v.execute({'name':Hello()}, {}),
                          'Fetch name')
        escape_me = '<John & "qouted\'>'
        self.assertEquals(u'&lt;John &amp; &quot;qouted&#39;&gt;',
                          v.execute({'name': escape_me}, {}),
                          'Escape data')
        self.assertEquals(escape_me,
                  v.execute({'name': escape_me}, {'escape': False}),
                  'Check safe')

    def test_parse_variable(self):
        """ Test variable token parsing """
        self.assertEquals('name', VariableToken.validate('{name}', self.language).name, 'Parse variable')
        self.assertEquals(None, VariableToken.validate('str', self.language), 'String is not valid')
        self.assertEquals(None, VariableToken.validate('{a|b}', self.language), 'Ignore rules syntax')
        self.assertEquals(None, VariableToken.validate('{a||b}', self.language), 'Ignore piped syntax')
        self.assertEquals(None, VariableToken.validate('{a::b}', self.language), 'Ignore dotted')

    def test_execute_rules(self):
        """ Execute rules """
        token = RulesToken('name', 'somerule', self.language)
        self.assertEquals('somerule', token.execute({'name':'Jonh'}, {}), 'Execute token')

    def test_parse_rules(self):
        """ Test rules token parsing """
        rules = 'some text with any signs, including :.. and | to'
        v = RulesToken.validate('{count|%s}' % rules, self.language)
        self.assertEquals(v.name, 'count')
        self.assertEquals(v.rules, rules)
        self.assertEquals(None, RulesToken.validate('{name}', self.language), 'Do not works with variable')
        self.assertEquals(None, RulesToken.validate('{name||rule}', self.language), 'Do not works with pipe')

    def test_execute_piped(self):
        """ Execute piped token """
        v =PipeToken('name', 'somerule', self.language)
        self.assertEquals('John somerule', v.execute({'name':'John'},{}), 'Execute piped token')

    def test_parse_piped(self):
        v = PipeToken.validate('{name||rule}', self.language)
        self.assertEquals(v.__class__, PipeToken, 'Check is pipe token')

    def test_token_matcher(self):
        """ Token matcher """
        m = TokenMatcher([TextToken, VariableToken, PipeToken, RulesToken, CaseToken])
        self.assertEquals(TextToken, m.build_token('Hello', self.language).__class__, 'Test plain text')
        self.assertEquals(VariableToken, m.build_token('{name}', self.language).__class__, 'Test {name}')
        self.assertEquals(RulesToken, m.build_token('{name|rule}', self.language).__class__, 'Test {name|rule}')
        self.assertEquals(PipeToken, m.build_token('{name||rule}', self.language).__class__, 'Test {name||rule}')
        self.assertEquals(CaseToken, m.build_token('{name::upper}', self.language).__class__, 'Test {name::rule}')
        with self.assertRaises(InvalidTokenSyntax) as context:
            m.build_token('{invalid~token}', self.language)
        self.assertEquals('Token syntax is not supported for token "{invalid~token}"', str(context.exception), 'Check exception message')

    def test_variable_token(self):
        token = VariableToken(name = 'user')
        self.assertEquals('John', token.execute({'user':'John'}, {}), 'Pass string')
        self.assertEquals('John', token.execute({'user': Gender.male('John')}, {}), 'Pass Gender')
        self.assertEquals('John', token.execute({'user': {'name':'John'}},{}), 'Pass dict')
        self.assertEquals('John', token.execute({'user': {'title':'John'}},{}), 'Pass string')

    def test_rules_token(self):
        cm = ContextsMock()
        token = RulesToken(name = 'obj', rules = None, language = ContextsMock())
        self.assertEquals(cm.execute(None, cm), token.execute({'obj': cm}, {}), 'Test object passed to RulesToken')

    def test_case_token(self):
        token = CaseToken(name = 'obj', case = 'upper', language = self.language)
        self.assertEquals('HELLO', token.execute({'obj':'Hello'}, {}), 'Test case token')

if __name__=='__main__':
    unittest.main()

