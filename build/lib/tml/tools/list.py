from __future__ import absolute_import
# encoding: UTF-8
from .template import Variable, Template
from ..strings import to_string
from . import Renderable, BasePreprocessor
import six

class List(Renderable):
    """ Display list """
    def __init__(self, items, limit = None, separator = ', ', last_separator = None, tpl = None):
        self.items = items
        self.limit = limit
        self.separator = to_string(separator)
        self.last_separator = to_string(last_separator) if last_separator else None
        self.tpl = tpl if not tpl is None else Variable()
        if isinstance(self.tpl, six.string_types):
            self.tpl = Template(self.tpl)

    def render(self, context):
        """ Convert to unicode 
            Args:
                context (Context): translation context
        """
        limit = len(self.items)
        if not self.limit is None:
            limit = min(limit, self.limit)
        if limit == 1:
            # only one element:
            return self.tpl(self.items[0])
        tpl = self.tpl.compile(context)
        if self.last_separator is None:
            return self.render_items(limit, tpl)
        return six.u('%s %s %s') % (self.render_items(limit - 1, tpl), context.tr(self.last_separator), tpl(self.items[limit-1]))

    @classmethod
    def from_list(self, items):
        return List(items, last_separator = 'and')

    def __iter__(self):
        return self.items

    def render_items(self, limit, tpl):
            return self.separator.join([tpl(item) for item in self.items[0:limit]])


def preprocess_lists(data, context):
    reserved_keys = ('last_separator', 'separator', 'limit', 'tpl')
    kwargs = {key:context[key] for key in reserved_keys if key in context}
    if type(data) is list:
        return List(data, **kwargs)
    return data


class ListPreprocessor(BasePreprocessor):

    reserved_keys = ('last_separator', 'separator', 'limit', 'tpl')

    def __init__(self, items, context=None):
        self.items = items
        self.context = context or {}

    def process(self):
        if not type(self.items) is list:
            return self.items
        kwargs = {key:self.context[key] for key in self.reserved_keys if key in self.context}
        return List(self.items, **kwargs)

