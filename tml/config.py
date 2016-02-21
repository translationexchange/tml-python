import logging
from copy import copy
from .base import Singleton
from .utils import APP_DIR, rel, merge


class BaseConfig(dict, Singleton):

    def init(self, **kwargs):
        self.init_config()
        self.override_config(**kwargs)

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

    def init_config(self):

        def is_builtin(k):
            return k.startswith('__') or k.endswith('__')
        def is_callable(k):
            return callable(getattr(self, k))

        for k, v in Config.__dict__.iteritems():
            if is_builtin(k) or is_callable(k):
                continue
            self[k] = v

    def override_config(self, **kwargs):
        for k, v in kwargs.iteritems():
            orig_v = getattr(self, k, getattr(Config, k))
            if orig_v:
                if isinstance(orig_v, dict):
                    v = merge(copy(orig_v), v)
                self[k] = v


class Config(BaseConfig):
    logger = {
        'enabled': True,
        'path': rel(APP_DIR, 'tml.log'),
        'level': logging.DEBUG
    }

    api_client = 'tml.api.client.Client'

    locale = {
        'default': 'en',
        'method': 'current_locale',
        'subdomain': False,
        'extension': False
    }

    agent = {
        'enabled': True,
        'type': 'agent',
        'cache':   86400  # timeout every 24 hours
    }

    data_preprocessors = ('tml.tools.list.preprocess_lists',)
    env_generators = ('tml.tools.viewing_user.get_viewing_user',)

    cache = {
        'enabled': False,
        #'adapter': 'file',
        #'path': 'a/b/c/snapshot.tar.gz'
    }

    @property
    def default_locale(self):
        return self.locale['default']


CONFIG = Config.instance()

def configure(**kwargs):
    global CONFIG
    if kwargs:
        CONFIG.override_config(**kwargs)
    return CONFIG


