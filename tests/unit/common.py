import os
from contextlib import contextmanager

FIXTURES_PATH = '%s/fixtures' % os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


@contextmanager
def override_config(**overrides):
    from tml.config import CONFIG
    before_dict = {key: CONFIG[key] for key in overrides}
    CONFIG.override_config(**overrides)
    yield
    CONFIG.override_config(**before_dict)
