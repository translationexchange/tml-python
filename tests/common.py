import os
from contextlib import contextmanager

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


def unittest_fixture(request, key, value):
    setattr(request.cls, key, value)