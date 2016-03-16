#######################################################################
#
# Method Token Forms
#
# {user.name}
# {user.name:gender}
#
#######################################################################
from __future__ import absolute_import
# encoding: UTF-8
import re
from .data import DataToken, Error
from .. import utils


__author__ = 'xepa4ep'


class MethodToken(DataToken):
    EXPRESSION = re.compile(
        r'(%?\{{1,2}\s*[\w]+\.\w*\s*(:\s*\w+)*\s*(::\s*\w+)*\s*\}{1,2})'
    )

    @utils.cached_property
    def key(self):
        return self.short_name.split('.')[0]

    @utils.cached_property
    def object_method_name(self):
        return self.short_name.split('.')[1]

    def token_value(self, obj, language, options=None):
        options = {} if options is None else options
        try:
            return self.sanitize(getattr(obj, self.object_method_name), obj, language, utils.merge_opts(options, safe=False))
        except AttributeError:
            self.error('Missing value for `%s` in `%s`', self.full_name, self.label)
