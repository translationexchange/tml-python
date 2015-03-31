# encoding: UTF-8

class Renderable(object):
    """ Item renderable in context """
    def __call__(self, context):
        return self.render(context)

    def render(self, context):
        raise NotImplemented()

def render_data(data, context):
    for key in data:
        if isinstance(data[key], Renderable):
            data[key] = data[key](context)
    return data