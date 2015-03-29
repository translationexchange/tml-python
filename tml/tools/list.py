# encoding: UTF-8
from .template import Variable


class List(object):
    """ Display list """
    def __init__(self, items, limit = None, separator = ', ', last_separator = None, tpl = None):
        self.items = items
        self.limit = limit
        self.separator = separator
        self.last_separator = last_separator
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
        if self.last_separator is None:
            return self.render_items(limit)
        return u'%s %s %s' % (self.render_items(limit - 1), context.tr(self.last_separator), self.tpl(self.items[limit-1]))

    def render_items(self, limit):
            return self.separator.join([self.tpl(item) for item in self.items[0:limit]])

