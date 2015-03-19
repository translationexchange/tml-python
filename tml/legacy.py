# encoding: UTF-8
from tml.token.parser import default_parser
from tml.token import TextToken, VariableToken, RulesToken, CaseToken, PipeToken
from tml.rules.options import fetch_default_arg
import re

def render_token(token):
    """ Render token to sprinf """
    token_type = type(token)
    if token_type is TextToken:
        return token.text
    elif token_type is VariableToken:
        return sprintf_token(token)
    elif token_type is RulesToken:
        return fetch_default_arg(token.rules)
    elif token_type is PipeToken:
        return u'%s %s' %(sprintf_token(token), fetch_default_arg(token.rules.rules))
    elif token_type is CaseToken:
        return sprintf_token(token)
    else:
        return unicode(token)


def sprintf_token(token):
    return '%%(%s)s' % token.name

def to_sprintf(tokens):
    """ Parse tokens and convert as printf template """
    return u''.join((render_token(token) for token in tokens))

def text_to_sprintf(text, language):
    return to_sprintf(default_parser.parse(text, language))

LEGACY_TOKENS = re.compile('\%\((\w+?)\)s')

def suggest_label(text):
    return re.sub(LEGACY_TOKENS, '{\\1}', text)

