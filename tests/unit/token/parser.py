import unittest
from tml.token import VariableToken, TextToken, RulesToken, PipeToken,\
    TokenMatcher, InvalidTokenSyntax, execute_all
from tml.token.parser import TokenParser, IS_TOKEN
from tests.unit.token import FakeLanguage
 

class TokenTest(unittest.TestCase):
    def test_parser(self):
        p = TokenParser(IS_TOKEN,
                        TokenMatcher([TextToken,
                                      VariableToken,
                                      RulesToken,
                                      PipeToken]))
        tokens = p.parse('{name} give you {count||apple} for free', FakeLanguage())
        self.assertEquals(4, len(tokens), 'Splited to 4 tokens')
        self.assertEquals(VariableToken, tokens[0].__class__, '{name} is varible')
        self.assertEquals(TextToken, tokens[1].__class__, '"give you" is text')
        self.assertEquals(' give you ', tokens[1].execute({}, {}), '" give you " with spaces')
        self.assertEquals(PipeToken, tokens[2].__class__, 'find pipe token')
        self.assertEquals('John give you 1 apple for free', execute_all(tokens, {'name':'John', 'count': 1}, {}))


if __name__=='__main__':
    unittest.main()