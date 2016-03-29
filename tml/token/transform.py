# encoding: UTF-8
#######################################################################
#
# Transform Token Form
#
# {count:number || one: message, many: messages}
# {count:number || one: сообщение, few: сообщения, many: сообщений, other: много сообщений}   in other case the number is not displayed#
#
# {count | message}   - will not include {count}, resulting in "messages" with implied {count}
# {count | message, messages}
#
# {count:number | message, messages}
#
# {user:gender | he, she, he/she}
#
# {user:gender | male: he, female: she, other: he/she}
#
# {now:date | did, does, will do}
# {users:list | all male, all female, mixed genders}
#
# {count || message, messages}  - will include count:  "5 messages"
#
#######################################################################

from __future__ import absolute_import
import re
import string
from .data import DataToken, Error
from .. import utils
from ..strings import to_string

__author__ = 'xepa4ep'

PIPE_CHAR = '|'
DBL_PIPE_CHAR = '||'
CASE_CHAR = '::'


class TransformToken(DataToken):
    pipe_separator = None
    piped_params = None

    EXPRESSION = re.compile(
        r'(%?\{{1,2}\s*[\w]+\s*(:\s*\w+)*\s*\|\|?[^\{\}\|]+\}{1,2})'
    )

    @property
    def system_name(self):
        return 'piped'

    def parse_elements(self):
        name_without_parens = self.full_name.lstrip('%')[1:-1]
        name_without_pipes = name_without_parens.split(PIPE_CHAR)[0].strip()
        name_without_case_keys = name_without_pipes.split(CASE_CHAR)[0].strip()
        self.short_name = name_without_pipes.split(':')[0].strip()
        self.case_keys = self.parse_cases(name_without_pipes)
        self.context_keys = self.parse_context_keys(name_without_pipes)
        try:
            self.pipe_separator = self.full_name.index(DBL_PIPE_CHAR) and DBL_PIPE_CHAR
        except ValueError:
            self.pipe_separator = PIPE_CHAR
        self.piped_params = name_without_parens.split(self.pipe_separator)[-1]

    def token_value_displayed(self):
        return self.pipe_separator == DBL_PIPE_CHAR

    def is_implied(self):
        return not self.token_value_displayed()

    def _substitute(self, label, context, language, options=None):
        options = {} if options is None else {}
        obj = self.token_object(context, self.key)
        language_context = None
        if not obj:
            self.error("Missing value for a token `%s` in `%s`\"", self.key, label)
        if not self.piped_params:
            self.error("Piped params may not be empty for token %s in %s", self.key, label)
        try:
            language_context = self.context_for_language(language)
        except:   # language context is absent, try to guess
            language_context = None
        value = language.contexts.execute(self.piped_params, obj, utils.merge_opts({}, language_context=language_context)).strip()
        if not value:
            return label
        cases = self.parse_cases(value)   # message::plural => messages
        if cases:
            value = self._apply_language_cases(cases, value.split('::')[0], obj, language, options)
        decorated_value = self.decorate(
            self.token_value(
                context.get(self.key, None),
                language,
                options),
            options)
        subst_value = []
        if self.token_value_displayed():
            subst_value.append(decorated_value)
            subst_value.append(' ')
        else:  # not include value: overwrite value with decorated one
            value = value.replace('#{}'.format(self.short_name), decorated_value)
        subst_value.append(value)
        return label.replace(self.full_name, ''.join(subst_value))
