# encoding: UTF-8
from .template import Variable
from ..strings import to_string

class Renderable(object):
    def render(self, context):
        raise NotImplemented()

class List(Renderable):
    """ Display list """
    def __init__(self, items, limit = None, separator = ', ', last_separator = None, tpl = None):
        self.items = items
        self.limit = limit
        self.separator = to_string(separator)
        self.last_separator = to_string(last_separator) if last_separator else None
        self.tpl = tpl if not tpl is None else Variable()

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
        return u'%s %s %s' % (self.render_items(limit - 1, tpl), context.tr(self.last_separator), tpl(self.items[limit-1]))

    def render_items(self, limit, tpl):
            return self.separator.join([tpl(item) for item in self.items[0:limit]])

