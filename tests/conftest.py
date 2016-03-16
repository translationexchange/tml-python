import pytest
import tml
from tml.context import LanguageContext
from tml.application import Application
from .common import unittest_fixture
from .mock import Client



@pytest.fixture(scope="class")
def build_context(request):
    """Force test suite to use language context directly.
    It is much easier to test translation functionality of individual key using LanguageContext in conjunction with mock.Client"""

    def _build_context(self, *args, **kwargs):
        if not kwargs.get('skip', False):
            kwargs['context'] = LanguageContext
        return tml.build_context(*args, **kwargs)
    return unittest_fixture(request, 'build_context', _build_context)


@pytest.fixture(scope="class")
def initialize(request):
    def _initialize(self, *args, **kwargs):
        if not kwargs.get('skip', False):
            kwargs['context'] = LanguageContext
        return tml.initialize(*args, **kwargs)
    return unittest_fixture(request, 'initialize', _initialize)


@pytest.fixture(scope='class')
def init_app(request):

    def _init_app(self):
        client = Client()
        client.read('projects/current/definition')
        app = Application.load_default(client)
        for locale in ('ru', 'en'):
            client.read('languages/{}'.format(locale))
            app.language(locale)
        return app
    return unittest_fixture(request, 'init_app', _init_app)
