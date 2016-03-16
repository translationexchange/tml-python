from __future__ import absolute_import
# encoding: UTF-8
import re
import six
from ..exceptions import Error as BaseError
from ..session_vars import get_current_context
from ..strings import to_string
from .. import utils

__author__ = 'xepa4ep'


def need_to_escape(options):
    """ Need escape string
        Args:
            options (dict): translation options
        Returns:
            boolean
    """
    if 'escape' in options:
        return options['escape']
    return True

def escape_if_needed(text, options):
    """ Escape string if it needed
        Agrs:
            text (string): text to escape
            options (dict): tranlation options (if key safe is True - do not escape)
        Returns:
            text
    """
    if hasattr(text, '__html__'):
        # Text has escape itself:
        return to_string(text.__html__())
    if need_to_escape(options):
        return escape(to_string(text))
    return to_string(text)

ESCAPE_CHARS = (('&', '&amp;'),
                ('<', '&lt;'),
                ('>', '&gt;'),
                ('"', '&quot;'),
                ("'", '&#39;'))

def escape(text):
    """ Escape text
        Args:
            text: input text
        Returns:
            (string): escaped HTML
    """
    for find, replace in ESCAPE_CHARS:
        text = text.replace(find, replace)
    return text

def is_language_cases_enabled():
    context = get_current_context()
    if not context:
        return False
    if not context.application:
        return False
    return context.application.feature_enabled('language_cases')


class Error(BaseError):
    pass


class DataToken(object):

    label = None
    full_name = None
    short_name = None
    case_keys = None
    context_keys = None

    EXPRESSION = re.compile(
        r'(%?\{{1,2}\s*\w+\s*(:\s*\w+)*\s*(::\s*\w+)*\s*\}{1,2})'
    )

    @classmethod
    def parse(cls, label, options=None):
        options = {} if options is None else options
        tokens = set()
        for match_item in cls.EXPRESSION.findall(label):
            tokens.add(cls(label, match_item[0]))
        return list(tokens)

    def __init__(self, label, token):
        self.label = label
        self.full_name = token
        self.parse_elements()

    @property
    def system_name(self):
        return self.__class__.__name__.lower()

    def parse_elements(self):
        name_without_parens = self.full_name.lstrip('%')[1:-1]
        name_without_case_keys = name_without_parens.split('::')[0].strip()
        self.short_name = name_without_parens.split(':')[0].strip()
        self.case_keys = self.parse_cases(name_without_parens)
        self.context_keys = self.parse_context_keys(name_without_case_keys)

    def name(self, options=None):
        options = {} if options is None else options
        ret = self.short_name
        if options.get('context_keys', False):
            ret = "%(val)s:%(context_keys)s" % {'val': ret, 'context_keys': ':'.join(self.context_keys)}
        if options.get('case_keys', False):
            ret = "%(val)s::%(cases)s" % {'val': ret, 'cases': '::'.join(self.case_keys)}
        if options.get('parens', False):
            ret = '{%s}' % ret
        return ret

    @property
    def key(self):
        return self.short_name

    def context_for_language(self, language):
        if self.context_keys:
            return language.contexts.find_by_code(self.context_keys[0])
        else:
            return language.contexts.find_by_token_name(self.short_name)

    def parse_cases(self, text):
        return list(case_key.lstrip('::') for case_key
                    in re.compile(r"(::\w+)").findall(text))

    def parse_context_keys(self, text):
        return list(key.lstrip(':') for key
                    in re.compile(r"(:\w+)").findall(text))


    ##############################################################################
      #
      # gets the value based on various evaluation methods
      #
      # examples:
      #
      # tr("Hello {user}", {'user': [current_user, current_user.name]}}
      # tr("Hello {user}", {'user': [current_user, ':name']}}
      #
      # tr("Hello {user}", {'user': [{'name': "Michael", 'gender': 'male'}, current_user.name]}}
      # tr("Hello {user}", {'user': [{'name': "Michael", 'gender': 'male'}, ':name']}}
      #
    ##############################################################################

    def token_value_from_array_param(self, array, language, options=None):
        options = {} if options is None else options
        if len(array) < 2:
            raise Error('Invalid value for array token `%s` in `%s`' % (self.full_name, self.label))
        if isinstance(array[0], list):
            raise Error("List tokens are not supported yet.")

        if not array[1].startswith(':'):   # already evaluated
            return self.sanitize(array[1], array[0], language, utils.merge_opts(options, safe=True))
        elif isinstance(array[0], dict):   # it is a dict
            try:
                return self.sanitize(array[0].get(array[1][1:]), array[0], language, utils.merge_opts(options, safe=False))
            except KeyError:
                raise Error('Invalid value for array token `%s` in `%s`' % (self.full_name, self.label))
        else:   # it is an object
            try:
                return self.sanitize(getattr(array[0], array[1][1:]), array[0], language, utils.merge_opts(options, safe=False))
            except AttributeError:
                raise Error('Invalid value for array token `%s` in `%s`' % (self.full_name, self.label))

    ##############################################################################
      #
      # examples:
      #
      # tr("Hello {user}", {'user': {'value': "Michael", 'gender': 'male'}}}
      #
      # tr("Hello {user}", {'user': {:object: {'gender': 'male'}, 'value': "Michael"}}}
      # tr("Hello {user}", {'user': {:object: {'name': "Michael", 'gender': 'male'}, 'property': 'name'}}}
      # tr("Hello {user}", {'user': {:object: {'name': "Michael", 'gender': :male}, 'attribute': 'name'}}}
      #
      # tr("Hello {user}", {'user': {'object': user, 'value': "Michael"}}}
      # tr("Hello {user}", {'user': {'object': user, 'property' 'name'}}}
      # tr("Hello {user}", {'user': {'object': user, :attribute: 'name'}}}
      #
    ##############################################################################

    def token_value_from_hash_param(self, the_hash, language, options=None):
        options = {} if options is None else options
        value = the_hash.get('value', None)
        obj = the_hash.get('object', None)
        if value:   # if value is present then evaluate immediately
            return self.sanitize(value, obj or the_hash, language, utils.merge_opts(options, safe=True))
        if not obj:   # if no object then nothing to evaluate. incorrect syntax
            raise Error("Missing value for hash token #{full_name} in #{label}")
        attr = the_hash.get('attribute', the_hash.get('property', None))
        if not attr:   # specified attr not set
            raise Error("Missing value for hash token #{full_name} in #{label}")
        if isinstance(obj, dict):   # if obj is dict, then access by key
            try:
                return self.sanitize(obj.get(attr), obj, language, utils.merge_opts(options, safe=False))
            except KeyError:
                raise Error("Missing value for hash token #{full_name} in #{label}")
        try:   # obj is object, so access by attribute
            return self.sanitize(getattr(obj, attr), obj, language, utils.merge_opts(options, safe=False))
        except AttributeError:
            raise Error("Missing value for hash token #{full_name} in #{label}")

    def apply_language_cases(self, value, obj, language, options=None):
        options = {} if options is None else options
        for case_key in self.case_keys:
            value = self.apply_case(case_key, value, obj, language, options)
        return value

    def apply_case(self, case_key, value, obj, language, options=None):
        options = {} if options is None else options
        lcase = language.case_by_keyword(case_key)
        return lcase.execute(value)

    # evaluate all possible methods for the token value and return sanitized result
    def token_value(self, obj, language, options=None):
        options = {} if options is None else options
        if isinstance(obj, list):
            return self.token_value_from_array_param(obj, language, options)
        if isinstance(obj, dict):
            return self.token_value_from_hash_param(obj, language, options)
        return self.sanitize(obj, obj, language, options)

    def sanitize(self, value, obj, language, options=None):
        options = {} if options is None else options
        value = str(value)
        ctx = get_current_context()
        if ctx and not ctx.block_option('skip_html_escaping'):
            value = escape_if_needed(value, options)
        if is_language_cases_enabled():
            return self.apply_language_cases(value, obj, language, options)
        return value

    def substitute(self, label, context, language, options=None):
        options = {} if options is None else options
        obj = context.get(self.key, None)
        if obj is None and not self.key in context:
            raise Error('Missing value for `%s` in `%s`' % (self.full_name, self.label))
        if obj is None:
            return label.replace(self.full_name, '')
        value = self.token_value(obj, language, options)
        return label.replace(self.full_name, self.decorate(value, options))

    def decorate(self, value, options=None):
        options = {} if options is None else options
        return value
