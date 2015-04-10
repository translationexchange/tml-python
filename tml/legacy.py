# encoding: UTF-8
from .token.parser import default_parser
from .token import TextToken, VariableToken, RulesToken, CaseToken, PipeToken
from .rules.options import fetch_default_arg
from .translation import Key
from .strings import to_string
import re
from tml.dictionary import TranslationIsNotExists


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
    return to_sprintf(default_parser.parse(to_string(text), language))

LEGACY_TOKENS = re.compile('\%\((\w+?)\)s')

def suggest_label(text):
    return re.sub(LEGACY_TOKENS, '{\\1}', text)

def translate(context, label, data, description, options):
    """ Tranlate with legacy
        Args:
            context (Context): current context
            label (str): tranlation label
            data (dict): user data
            options (dict): tranlation options
        Returns:
            text, key
    """
    t = fetch(context, label, description)
    o = t.fetch_option(data, options)
    # support %(name)s -> {name}
    o.label = suggest_label(o.label)
    return o.apply(data, options)

def execute(translation, data, options):
    """ Execute translation in legacy mode """
    o = translation.fetch_option(data, options)
    # support %(name)s -> {name}
    o.label = suggest_label(o.label)
    # apply translation:
    return o.apply(data, options)


def fetch(context, label, description):
    """ Fetch translation for old label """
    try:
        # Try to suggest translation replace %(name)s -> {name}
        return context.fetch(suggest_label(label), description)
    except TranslationIsNotExists:
        # Try to tranlate as is
        try:
            return context.fetch(label, description)
        except TranslationIsNotExists:
            return context.fallback(label, description)


        

