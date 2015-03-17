from django.template import (Node, Variable, TemplateSyntaxError,
    TokenParser, Library, TOKEN_TEXT, TOKEN_VAR)
from django.template.base import render_value_in_context
from django.template.defaulttags import token_kwargs
from ..__init__ import tr
from django.utils import six
from django.utils import six
import sys
from django.utils.translation.trans_real import trim_whitespace

register = Library()

class BlockTranslateNode(Node):

    def __init__(self, extra_context, content, message_context=None, trimmed=False):
        self.extra_context = extra_context
        self.message_context = message_context
        self.content = content

    def render_token_list(self, tokens):
        result = []
        vars = []
        for token in tokens:
            if token.token_type == TOKEN_TEXT:
                result.append(token.contents.replace('%', '%%'))
            elif token.token_type == TOKEN_VAR:
                result.append('{%s}' % token.contents)
                vars.append(token.contents)
        msg = ''.join(result)
        if self.trimmed:
            msg = trim_whitespace(msg)
        return msg, vars

    def render(self, context, nested=False):
        if self.message_context:
            message_context = self.message_context.resolve(context)
        else:
            message_context = None
        tmp_context = {}
        for var, val in self.extra_context.items():
            tmp_context[var] = val.resolve(context)
        # Update() works like a push(), so corresponding context.pop() is at
        # the end of function
        context.update(tmp_context)
        return tr(label = self.content, data = context, description = message_context)


@register.tag("tr")
def do_block_translate(parser, token):
    """
    This will translate a block of text with parameters.

    Usage::

        {% tr with bar=foo|filter boo=baz|filter %}
        This is {{ bar }} and {{ boo }}.
        {% endtr %}


    The "var as value" legacy format is still supported::

        {% blocktrans with foo|filter as bar and baz|filter as boo %}
        {% blocktrans count var|length as count %}

    Contextual translations are supported::

        {% blocktrans with bar=foo|filter context "greeting" %}
            This is {{ bar }}.
        {% endblocktrans %}

    This is equivalent to calling pgettext/npgettext instead of
    (u)gettext/(u)ngettext.
    """
    bits = token.split_contents()

    options = {}
    remaining_bits = bits[1:]
    while remaining_bits:
        option = remaining_bits.pop(0)
        if option in options:
            raise TemplateSyntaxError('The %r option was specified more '
                                      'than once.' % option)
        if option == 'with':
            value = token_kwargs(remaining_bits, parser, support_legacy=True)
            if not value:
                raise TemplateSyntaxError('"with" in %r tag needs at least '
                                          'one keyword argument.' % bits[0])
        elif option == "context":
            try:
                value = remaining_bits.pop(0)
                value = parser.compile_filter(value)
            except Exception:
                msg = (
                    '"context" in %r tag expected '
                    'exactly one argument.') % bits[0]
                six.reraise(TemplateSyntaxError, TemplateSyntaxError(msg), sys.exc_info()[2])
        elif option == "trimmed":
            value = True
        else:
            raise TemplateSyntaxError('Unknown argument for %r tag: %r.' %
                                      (bits[0], option))
        options[option] = value

    if 'context' in options:
        message_context = options['context']
    else:
        message_context = None
    extra_context = options.get('with', {})

    trimmed = options.get("trimmed", False)

    content = []
    while parser.tokens:
        token = parser.next_token()
        if token.token_type in (TOKEN_VAR, TOKEN_TEXT):
            content.append(token)
        else:
            break

    if token.contents.strip() != 'endtr':
        raise TemplateSyntaxError("'tr' doesn't allow other block tags (seen %r) inside it" % token.contents)

    return BlockTranslateNode(extra_context, content, message_context, trimmed=trimmed)

