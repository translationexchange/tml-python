# -*- coding: utf-8 -*-
from __future__ import absolute_import
# encoding: UTF-8
import re
import six
from ..exceptions import Error as BaseError
from ..session_vars import get_current_context
from ..strings import to_string
from .. import utils
from ..logger import LoggerMixin
from ..config import CONFIG
from tml.native_decoration import get_decorator

__author__ = 'xepa4ep'


def need_to_escape(options):
    """ Need escape string
        Args:
            options (dict): translation options
        Returns:
            boolean
    """
    ctx = get_current_context()
    if ctx and not ctx.block_option('skip_html_escaping'):
        if 'escape' in options:
            return options['escape']
        if 'safe' in options:
            return not options['safe']
    return False

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


class DataToken(LoggerMixin):

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
        self.label = to_string(label)
        self.full_name = to_string(token)
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
      # {% tr with user=some_user|name user-format="[user.name]" %}
      # {% endtr %}
      # tr("Hello {user}", {'user': [current_user, current_user.name]}}
      # tr("Hello {user}", {'user': [current_user, ':name']}}
      #
      # tr("Hello {user}", {'user': [{'name': "Michael", 'gender': 'male'}, current_user.name]}}
      # tr("Hello {user}", {'user': [{'name': "Michael", 'gender': 'male'}, ''name'']}}
      #
    ##############################################################################

    def token_value_from_array_param(self, array, language, options=None):
        options = {} if options is None else options
        if len(array) < 2:
            self.error('Invalid value for array token `%s` in `%s`', self.full_name, self.label)
        if isinstance(array[0], list):
            return self.token_values_from_array(array, language, options)
        if not array[1].startswith(':'):   # already evaluated
            return self.sanitize(array[1], array[0], language, utils.merge_opts(options, safe=True))
        elif isinstance(array[0], dict):   # it is a dict
            try:
                return self.sanitize(array[0].get(array[1][1:]), array[0], language, utils.merge_opts(options, safe=False))
            except KeyError:
                self.error('Invalid value for array token `%s` in `%s`', self.full_name, self.label)
        else:   # it is an object
            try:
                return self.sanitize(getattr(array[0], array[1][1:]), array[0], language, utils.merge_opts(options, safe=False))
            except AttributeError:
                self.error('Invalid value for array token `%s` in `%s`', self.full_name, self.label)

    ##############################################################################
      #
      # tr("Hello {user_list}!", "", {'user_list': [[user1, user2, user3], ':name']}}
      #
      # first element is an array, the rest of the elements are similar to the
      # property, string, with parameters that follow
      #
      # if you want to pass options, then make the second parameter an array as well
      #
      # tr("{users} joined the site", {'users': [[user1, user2, user3], ':name']})
      #
      #
      # tr("{users} joined the site", {'users': [[user1, user2, user3], {'attribute': 'name'})
      #
      # tr("{users} joined the site", {'users': [[user1, user2, user3], 'attribute': 'name', 'value': "<strong>{$0}</strong>"})
      #
      # tr("{users} joined the site", {'users': [[user1, user2, user3], "<strong>{$0}</strong>")
      #
      #
      ##############################################################################

    def token_values_from_array(self, params, language, options, context=None):
        context = context or get_current_context()
        tpl_sign = "{$0}"
        default_list_options = {
            'description': 'List joiner',
            'limit': 7,
            'separator': ', ',
            'joiner': 'and',
            #'less': '{laquo} less',  # todo: add fn
            #'expandable': True,  # todo: add fn
            #'collapsable': True   # todo: add fn
        }
        objects = params[0]
        method = params[1]
        if len(params) > 2:
            list_options = utils.merge_opts(default_list_options, **params[2])
        else:
            list_options = utils.merge_opts(default_list_options, **{})

        def render_element(obj):
            element = ''
            if isinstance(method, six.string_types):
                if not method.startswith(':'):
                    element = method.replace(tpl_sign, self.sanitize(to_string(obj), obj, language, utils.merge_opts(options, safe=False)))
                else:
                    if isinstance(obj, dict):
                        value = obj.get(method[1:], '')
                    else:
                        value = getattr(obj, method[1:], '')
                    element = self.sanitize(value, obj, language, utils.merge_opts(options, safe=False))
            elif isinstance(method, dict):
                attr = method.get('attribute', method.get('property', None))
                if isinstance(obj, dict):
                    value = obj.get(attr, '')
                else:
                    value = getattr(obj, attr, '')
                forced_value = method.get('value', None)
                if forced_value:
                    element = forced_value.replace(tpl_sign, self.sanitize(value, obj, language, utils.merge_opts(options, safe=False)))
                else:
                    element = self.sanitize(value, obj, language, utils.merge_opts(options, safe=False))
            else:  # use object by default (may be it just string)
                element = obj
            decorator = get_decorator()
            return decorator.decorate_element(element, options)

        def build_str(limit, sep, joiner):
            builder = []
            builder.append(sep.join(values[0:limit]))
            builder.append(joiner)
            builder.append(values[limit])
            return to_string(" ").join(builder)

        values = list(map(render_element, objects))   # in py3 map returns iterator
        if len(objects) == 1:
            return values[0]
        if not list_options.get('joiner', ''):
            return list_options['separator'].join(values)
        joiner = list_options['joiner']
        if context: # translate joiner if context configured
            context.push_options(dict(target_locale=language.locale))
            _, joiner, _ = context.tr(list_options['joiner'],
                                description=list_options['description'],
                                data={},
                                options=options)
            context.pop_options()

        if len(values) <= list_options['limit']:
            return build_str(-1, list_options['separator'], joiner)
        return build_str(list_options['limit'] - 1, list_options['separator'], joiner)

    def token_value_from_hash_param(self, the_hash, language, options=None):
        options = {} if options is None else options
        value = the_hash.get('value', None)
        obj = the_hash.get('object', None)
        if value:   # if value is present then evaluate immediately
            return self.sanitize(value, obj or the_hash, language, utils.merge_opts(options, safe=True))
        if not obj:   # if no object then nothing to evaluate. incorrect syntax
            self.error("Missing value for hash token `%s` in `%s`", self.full_name, self.label)
        attr = the_hash.get('attribute', the_hash.get('property', None))
        if not attr:   # specified attr not set
            self.error("Missing value for hash token `%s` in `%s`", self.full_name, self.label)
        if isinstance(obj, dict):   # if obj is dict, then access by key
            try:
                return self.sanitize(obj.get(attr), obj, language, utils.merge_opts(options, safe=False))
            except KeyError:
                self.error("Missing value for hash token `%s` in `%s`", self.full_name, self.label)
        try:   # obj is object, so access by attribute
            return self.sanitize(getattr(obj, attr), obj, language, utils.merge_opts(options, safe=False))
        except AttributeError:
            self.error("Missing value for hash token `%s` in `%s`", self.full_name, self.label)

    def apply_language_cases(self, value, obj, language, options=None):
        options = {} if options is None else options
        return self._apply_language_cases(self.case_keys, value, obj, language, options)


    def _apply_language_cases(self, case_keys, value, obj, language, options=None):
        for case_key in case_keys:
            value = self.apply_case(case_key, value, obj, language, options)
        return value

    def apply_case(self, case_key, value, obj, language, options=None):
        options = {} if options is None else options
        lcase = language.case_by_keyword(case_key)
        return lcase and lcase.execute(value) or value

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
        value = escape_if_needed(value, options)
        if is_language_cases_enabled():
            return self.apply_language_cases(value, obj, language, options)
        return value

    def substitute(self, label, context, language, options=None):
        label = to_string(label)
        try:
            return self._substitute(label, context, language, options)
        except Error as e:
            self.exception(e)
            CONFIG.handle_exception(e)
            return label

    def _substitute(self, label, context, language, options):
        options = {} if options is None else options
        obj = context.get(self.key, None)
        if obj is None and not self.key in context:
            self.error('Missing value for `%s` in `%s`', self.full_name, self.label)
        if obj is None:
            return label.replace(self.full_name, '')
        value = self.token_value(obj, language, options)
        return label.replace(self.full_name, self.decorate(value, options))

    def decorate(self, value, options=None):
        options = {} if options is None else options
        decorator = get_decorator()
        return decorator.decorate_token(self, value, options)

    @classmethod
    def token_object(cls, token_values, token_name):
        if not token_values:
            return None
        token_object = token_values.get(token_name, None)
        if isinstance(token_object, list): # if list then return first el
            return token_object[0]
        if isinstance(token_object, dict):  # if dict access `object` key
            obj = token_object.get('object', None)
            if obj:
                return obj
        return token_object

    def decoration_name():
        return 'html'

    def error(self, msg, *params):
        raise Error(to_string(msg) % params)
