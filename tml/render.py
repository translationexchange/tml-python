# encoding: UTF-8
from .decoration.parser import parse
from .tools import Renderable
from argparse import ArgumentError

class RenderEngine(object):
    """ Engine to render translations """
    # List of objects which preprocess data before translation (join lists for example)
    data_preprocessors = []
    # List of objects which add custom values to data (like viewing_user)
    env_generators = []

    def render(self, translation, data, options):
        """ Render translation 
            Args:
                translation (Transaltion): translation to render
                data (dict): user data
                options (dict): transaltion options
            Returns:
                unicode
        """
        # Apply tokens:
        ret = translation.execute(self.prepare_data(data), options)
        # Apply decoration:
        return parse(ret).render(options)

    def prepare_data(self, data):
        """ Render engine """
        return Data(data, self)


class Data(object):
    """ Some data can be prerendered with current context """
    def __init__(self, data, context):
        """ .ctor
            data (dict): user data
            context (tml.Context): translation context (current language etc.)
        """
        self.data = data if data else {}
        self.context = context

    def __getitem__(self, key, *args, **kwargs):
        try:
            # get item for data:
            ret = self.data[key]
        except KeyError as e:
            return self.generate_item(key)
        for p in self.context.data_preprocessors:
            # preprocess data ([] -> List etc)
            ret = p(ret, self.context)
        # Apply renderable data:
        if isinstance(ret, Renderable):
            ret = ret.render(self.context)
        return ret

    def generate_item(self, key):
        """ Generate item for key """
        for g in self.context.env_generators:
            try:
                ret = g(key, self.context, self.data)
                if not ret is None:
                    return ret
            except ArgumentError:
                pass
        raise KeyError('%s key is not found in translation data' % key) 

