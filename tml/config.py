import logging
from copy import copy
from six import iteritems, reraise
import sys
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

    def __len__(self):
        return len(self.__dict__)

    def get(self, key, default=None):
        return self.__dict__.get(key.lower(), default)

    def init_config(self):

        def is_builtin(k, v):
            return k.startswith('__') or k.endswith('__')

        def is_callable(k, v):
            return callable(v)

        for k, v in iteritems(Config.__dict__):
            if is_builtin(k, v) or is_callable(k, v):
                continue
            self[k] = v

    def override_config(self, **kwargs):
        for k, v in iteritems(kwargs):
            orig_v = getattr(self, k, getattr(Config, k))
            if orig_v is not None:
                if isinstance(orig_v, dict):
                    v = merge(copy(orig_v), v)
                self[k] = v

class Config(BaseConfigMixin, Singleton):

    def __init__(self, *a, **kw):
        Singleton.__init__(self, *a, **kw)

    def init(self, **kwargs):
        self.init_config()
        self.override_config(**kwargs)

    app_dir = APP_DIR

    environment = 'dev'

    verbose = False

    application = {
        #'key':
        #'token'
        #"path": 'https://staging-api.translationexchange.com'
        #"cdn_path": "http://trex-snapshots.s3-us-west-1.amazonaws.com"
        "path": "https://api.translationexchange.com",
        "cdn_path": "http://cdn.translationexchange.com"
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
        'extension': False,
        'query_param': 'locale'
    }

    locale_mapping = {
        'pt-br': 'pt-BR',
        'zh-hans-cn': 'zh-Hans-CN'
    }

    agent = {
        'enabled': True,
        'type': 'agent',
        'cache':   86400,  # timeout every 24 hours
        'host': "https://tools.translationexchange.com/agent/stable/agent.min.js",
        'force_injection': False    # force inject js agent as soon as tml is configured
        #'host': "https://tools.translationexchange.com/agent/staging/agent.min.js"
    }

    data_preprocessors = ()
    env_generators = ('tml.tools.viewing_user.get_viewing_user',)

    cache = {
        'enabled': False,
        #'adapter': 'file',
        #'path': 'a/b/c/snapshot.tar.gz'
    }

    default_source = "index"

    context_class = None   # just for testing purpose

    context_rules = {
        'number': {'variables': {}},
        'gender': {
            'variables': {
                '@gender': 'gender',
                '@size': lambda lst: len(lst)
            }
        },
        'genders': {
            'variables': {
                '@genders': lambda lst: [u['gender'] if hasattr(u, 'items') else getattr(u, 'gender') for u in lst]
            }
        },
        'date': {'variables': {}},
        'time': {'variables': {}},
        'list': {
            'variables': {
                '@count': lambda lst: len(lst)
            }
        }
    }

    localization = {
        'default_day_names'       :  ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        'default_abbr_day_names'  :  ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        'default_month_names'     :  ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        'default_abbr_month_names':  ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        'custom_date_formats'     :  {
          'default'               : '%m/%d/%Y',            # 07/4/2008
          'short_numeric'         : '%m/%d',               # 07/4
          'short_numeric_year'    : '%m/%d/%y',            # 07/4/08
          'long_numeric'          : '%m/%d/%Y',            # 07/4/2008
          'verbose'               : '%A, %B %d, %Y',       # Friday, July  4, 2008
          'monthname'             : '%B %d',               # July 4
          'monthname_year'        : '%B %d, %Y',           # July 4, 2008
          'monthname_abbr'        : '%b %d',               # Jul 4
          'monthname_abbr_year'   : '%b %d, %Y',           # Jul 4, 2008
          'date_time'             : '%m/%d/%Y at %H:%M',   # 01/03/1010 at 5:30
        },
        'token_mapping': {
          '%a': '{short_week_day_name}',
          '%A': '{week_day_name}',
          '%b': '{short_month_name}',
          '%B': '{month_name}',
          '%p': '{am_pm}',
          '%d': '{days}',
          '%e': '{day_of_month}',
          '%j': '{year_days}',
          '%m': '{months}',
          '%W': '{week_num}',
          '%w': '{week_days}',
          '%y': '{short_years}',
          '%Y': '{years}',
          '%l': '{trimed_hour}',
          '%H': '{full_hours}',
          '%I': '{short_hours}',
          '%M': '{minutes}',
          '%S': '{seconds}',
          '%s': '{since_epoch}'
        }
    }

    translator_options = {
        'debug': False,
        'debug_format_html': "<span style='font-size:20px;color:red;'>{</span> {$0} <span style='font-size:20px;color:red;'>}</span>",
        'debug_format': '{{{{$0}}}}',
        'split_sentences': False,
        'nodes': {
          'ignored':    [],
          'scripts':    ["style", "script", "code", "pre"],
          'inline':     ["a", "span", "i", "b", "img", "strong", "s", "em", "u", "sub", "sup"],
          'short':      ["i", "b"],
          'splitters':  ["br", "hr"]
        },
        'attributes': {
          'labels':     ["title", "alt"]
        },
        'name_mapping': {
          'b':    'bold',
          'i':    'italic',
          'a':    'link',
          'img':  'picture'
        },
        'data_tokens': {
          'special': {
            'enabled': True,
            'regex': '(&[^;]*;)'
          },
          'date': {
            'enabled': True,
            'formats': [
              ['((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+,\s+\d+)', "{month} {day}, {year}"],
              ['((January|February|March|April|May|June|July|August|September|October|November|December)\s+\d+,\s+\d+)', "{month} {day}, {year}"],
              ['(\d+\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec),\s+\d+)', "{day} {month}, {year}"],
              ['(\d+\s+(January|February|March|April|May|June|July|August|September|October|November|December),\s+\d+)', "{day} {month}, {year}"]
            ],
            'name': 'date'
          },
          'rules': [
            {'enabled': True, 'name': 'time',     'regex': '(\d{1,2}:\d{1,2}\s+([A-Z]{2,3}|am|pm|AM|PM)?)'},
            {'enabled': True, 'name': 'phone',    'regex': '((\d{1}-)?\d{3}-\d{3}-\d{4}|\d?\(\d{3}\)\s*\d{3}-\d{4}|(\d.)?\d{3}.\d{3}.\d{4})'},
            {'enabled': True, 'name': 'email',    'regex': '([-a-z0-9~!$%^&*_=+}{\'?]+(\.[-a-z0-9~!$%^&*_=+}{\'?]+)*@([a-z0-9_][-a-z0-9_]*(\.[-a-z0-9_]+)*\.(aero|arpa|biz|com|coop|edu|gov|info|int|mil|museum|name|net|org|pro|travel|io|mobi|[a-z][a-z])|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,5})?)'},
            {'enabled': True, 'name': 'price',    'regex': '(\$\d*(,\d*)*(\.\d*)?)'},
            {'enabled': True, 'name': 'fraction', 'regex': '(\d+\/\d+)'},
            {'enabled': True, 'name': 'num',      'regex': '\\b(\d+(,\d*)*(\.\d*)?%?)\\b'}
          ]
        }
    }

    # memcached
    #'cache': {
        #'enabled': True,
        #'adapter': 'memcached',
        #'backend': 'default',
       # 'namespace': 'foody'
    #},

    version_check_interval = 3600

    source_separator = '@:@'

    strict_mode = False

    supported_tr_opts = ('source',
                         'target_locale',)

    tml_cookie = 'trex_%s'

    decorator_class = "html"

    @property
    def default_locale(self):
        return self.locale['default']

    def get_locale(self, locale):
        if not locale:
            return self.default_locale
        return self.locale_mapping.get(locale, locale)

    def cache_enabled(self):
        return self['cache'].get('enabled', False)

    def application_key(self):
        return self['application'].get('key', 'current')

    def access_token(self, default=None):
        return self['application'].get('access_token', default)

    def api_host(self):
        return self.application['path']
        if self.environment == 'prod':
            return 'https://api.translationexchange.com'
        else:
            return

    def cdn_host(self):
        return self.application['cdn_path']

    def agent_host(self):
        return self.agent['host']

    def is_interactive_mode(self):
        return False

    def get_custom_date_format(self, format):
        return self.localization['custom_date_formats'][format]

    def strftime_symbol_to_token(self, symbol):
        return self.localization['token_mapping'].get(symbol, None)

    def get_abbr_day_name(self, index):
        return self.localization['default_abbr_day_names'][index]

    def get_day_name(self, index):
        return self.localization['default_day_names'][index]

    def get_abbr_month_name(self, index):
        return self.localization['default_abbr_month_names'][index]

    def get_month_name(self, index):
        return self.localization['default_month_names'][index]

    def handle_exception(self, exc):
        if self.strict_mode:
            reraise(exc.__class__, exc, sys.exc_info()[2])
        else:
            pass   # silent (logged in tml.py)

    def nested_value(self, hash_value, key, default_value=None):
        parts = key.split('.')
        for part in parts:
            if not hash_value.get(part, None):
                return default_value
            hash_value = hash_value.get(part)

        return hash_value

    def translator_option(self, key):
        return self.nested_value(self.translator_options, key)

CONFIG = Config.instance()

def configure(**kwargs):
    global CONFIG
    if kwargs:
        CONFIG.override_config(**kwargs)
    return CONFIG


