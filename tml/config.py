import logging
from copy import copy
from .base import Singleton
from .utils import APP_DIR, rel, merge


class BaseConfigMixin(dict):

    def __setitem__(self, key, value):
        self.__dict__[key.lower()] = value

    def __getitem__(self, key):
        return self.__dict__[key.lower()]

    def __delitem__(self, key):
        del self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    def get(self, key, default=None):
        return self.__dict__.get(key.lower(), default)

    def init_config(self):

        def is_builtin(k, v):
            return k.startswith('__') or k.endswith('__')

        def is_callable(k, v):
            return callable(v)

        for k, v in Config.__dict__.iteritems():
            if is_builtin(k, v) or is_callable(k, v):
                continue
            self[k] = v

    def override_config(self, **kwargs):
        for k, v in kwargs.iteritems():
            orig_v = getattr(self, k, getattr(Config, k))
            if orig_v is not None:
                if isinstance(orig_v, dict):
                    v = merge(copy(orig_v), v)
                    # print merge(copy(orig_v), v)
                self[k] = v

class Config(BaseConfigMixin, Singleton):

    def __init__(self, *a, **kw):
        Singleton.__init__(self, *a, **kw)

    def init(self, **kwargs):
        self.init_config()
        self.override_config(**kwargs)

    app_dir = APP_DIR

    environment = 'dev'

    application = {
        #'key':
        #'token'
    }

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

    version_check_interval = 3600

    @property
    def default_locale(self):
        return self.locale['default']

    def cache_enabled(self):
        return self['cache'].get('enabled', False)

    def application_key(self):
        return self['application'].get('key', 'current')


CONFIG = Config.instance()

def configure(**kwargs):
    global CONFIG
    if kwargs:
        CONFIG.override_config(**kwargs)
    return CONFIG


