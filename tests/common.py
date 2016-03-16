import os
import six
from hashlib import md5
from tml.strings import to_string
from contextlib import contextmanager
from tml.translation import Key
from tml.rules.contexts.gender import Gender


FIXTURES_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')


@contextmanager
def override_config(**overrides):
    from tml.config import CONFIG
    before_dict = {key: CONFIG[key] for key in overrides}
    CONFIG.override_config(**overrides)
    yield
    CONFIG.override_config(**before_dict)


class FakeLanguage(object):

    application = None

    def __init__(self):
        self.contexts = self
        self.cases = {'dat': CaseMock()}

    def execute(self, rule, value):
        return rule


class ContextsMock(object):
    """ Stupid class to test context matching """
    @property
    def contexts(self):
        return self

    def execute(self, rules, data):
        return data.__class__.__name__


class CaseMock(object):
    def execute(self, data):
        return data.upper()


class FakeUser(object):

    first_name = 'Tom'
    last_name = 'Anderson'
    gender = 'male'

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def __str__(self):
        return self.first_name + " " + self.last_name


def unittest_fixture(request, key, value):
    setattr(request.cls, key, value)

def build_key(label, language, description='', md5=None):
    key = Key(label=label, description=description, language=language)
    key_md5 = md5 or gen_key_md5(label, description)
    return key, "translation_keys/%s/translations" % key_md5

def gen_key_md5(label, description=''):
    key = six.u('%s;;;%s') % (to_string(label), to_string(description))
    ret = md5(key.encode('utf-8')).hexdigest()
    return ret

def male(value):
    return Gender.male(value)

def female(value):
    return Gender.female(value)
