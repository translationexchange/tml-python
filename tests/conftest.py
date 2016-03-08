import pytest
import tml
from tml.context import LanguageContext
from .common import unittest_fixture


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