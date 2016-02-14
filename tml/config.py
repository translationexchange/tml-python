import logging
from copy import copy
from .base import Singleton
from .utils import APP_DIR, rel, merge


class BaseConfig(dict, Singleton):

    def __init__(self, **kwargs):
        if getattr(self, 'configured', False):
            return
        self.init_config()
        self.override_config(**kwargs)
        self.configured = True

    def __setitem__(self, name, value):
        super(BaseConfig, self).__setitem__(name.lower(), value)

    def __setattr__(self, name, value):
        self[name.lower()] = value

    def __getattr__(self, name):
        name = name.lower()
        if name in self:
            return self[name]
        raise AttributeError

    def __delattr__(self, name):
        name = name.lower()
        del self[name]

    @classmethod
    def instance(cls, **kwargs):
        return Config(**kwargs)

    def init_config(self):

        def is_builtin(k):
            return k.startswith('__') or k.endswith('__')
        def is_callable(k):
            return callable(getattr(self, k))

        for k, v in Config.__dict__.iteritems():
            if is_builtin(k) or is_callable(k):
                continue
            self.__setattr__(k, v)


    def override_config(self, **kwargs):
        for k, v in kwargs.iteritems():
            orig_v = getattr(self, k, getattr(Config, k))
            if orig_v:
                if isinstance(orig_v, dict):
                    v = merge(copy(orig_v), v)
                self.__setattr__(k, v)


class Config(BaseConfig):
    logger = {
        'enabled': True,
        'path': rel(APP_DIR, 'tml.log'),
        'level': logging.DEBUG
    }
    api_client_class = 'tml.api.client.Client'


    