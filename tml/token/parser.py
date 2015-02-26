# encoding: UTF-8
import re
from tml.token import TokenMatcher, data_matcher


IS_TOKEN = re.compile('(\{.*?\})')

class TokenParser(object):
    """ Text parser """
    def __init__(self, regexp, supported_tokens):
        """ Token parser 
            Args:
                regexp (_sre.SRE_Pattern): token regext
                supported_tokens (TokenMatcher): token matcher 
        """
        self.regexp = regexp
        self.supported_tokens = supported_tokens

    def parse(self, text, language):
        return [self.supported_tokens.build_token(part, language) for part in self.regexp.split(text) if len(part)]


parser = TokenMatcher(IS_TOKEN, data_matcher)
