# encoding: UTF-8

class Renderable(object):
    """ Item renderable in context """
    def __call__(self, context):
        return self.render(context)

    def render(self, context):
        raise NotImplemented()
