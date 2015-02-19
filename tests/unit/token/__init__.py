import unittest
from tml.token import VariableToken, TextToken, RulesToken, PipeToken,\
    TokenMatcher, InvalidTokenSyntax


class LenRulesCompiler(object):
    """ Dumb rules compiller """
    def compile(self, token, value, options):
        self.value = value
        return self

    def execute(self):
        """ Say Hello """
        return '%d symbols' % len(self.value)

RulesToken.rules_compiller = LenRulesCompiler()

class TokenTest(unittest.TestCase):
    """ Test client """
    def test_execute_variable(self):
        v = VariableToken('name')
        self.assertEquals('John', v.execute({'name':'John'}, {}), 'Fetch name')
        class Hello(object):
            def __str__(self, *args, **kwargs):
                return 'Hello'
        self.assertEquals(u'Hello', v.execute({'name':Hello()}, {}), 'Fetch name')

    def test_parse_variable(self):
        """ Test variable token parsing """
        self.assertEquals('name', VariableToken.validate('{name}').name, 'Parse variable')
        self.assertEquals(None, VariableToken.validate('str'), 'String is not valid')
        self.assertEquals(None, VariableToken.validate('{a|b}'), 'Ignore rules syntax')
        self.assertEquals(None, VariableToken.validate('{a||b}'), 'Ignore piped syntax')
        self.assertEquals(None, VariableToken.validate('{a::b}'), 'Ignore dotted')

    def test_execute_rules(self):
        """ Execute rules """
        token = RulesToken('name', 'somerule')
        self.assertEquals('4 symbols', token.execute({'name':'Jonh'}, {}), 'Execute token')

    def test_parse_rules(self):
        """ Test rules token parsing """
        rules = 'some text with any signs, including :.. and | to'
        v = RulesToken.validate('{count|%s}' % rules)
        self.assertEquals(v.name, 'count')
        self.assertEquals(v.rules, rules)
        self.assertEquals(None, RulesToken.validate('{name}'), 'Do not works with variable')
        self.assertEquals(None, RulesToken.validate('{name||rule}'), 'Do not works with pipe')

    def test_execute_piped(self):
        """ Execute piped token """
        PipeToken.rules_compiller = LenRulesCompiler()
        v =PipeToken('name', 'somerule')
        self.assertEquals('John 4 symbols', v.execute({'name':'John'},{}), 'Execute piped token')

    def test_parse_piped(self):
        v = PipeToken.validate('{name||rule}')
        self.assertEquals(v.__class__, PipeToken, 'Check is pipe token')

    def test_token_matcher(self):
        """ Token matcher """
        m = TokenMatcher([TextToken, VariableToken, PipeToken, RulesToken])
        self.assertEquals(TextToken, m.build_token('Hello').__class__, 'Test plain text')
        self.assertEquals(VariableToken, m.build_token('{name}').__class__, 'Test {name}')
        self.assertEquals(RulesToken, m.build_token('{name|rule}').__class__, 'Test {name|rule}')
        self.assertEquals(PipeToken, m.build_token('{name||rule}').__class__, 'Test {name||rule}')
        with self.assertRaises(InvalidTokenSyntax) as context:
            m.build_token('{invalid~token}')
        self.assertEquals('Token syntax is not supported for token "{invalid~token}"', str(context.exception), 'Check exception message')


if __name__=='__main__':
    unittest.main()

