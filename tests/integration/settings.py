import os
from ..common import FIXTURES_PATH
pj = os.path.join

TML = {
    'environment': 'test',
    'application': {'key': '600d6ee64b2c59db3b1244e04ab42c92e50c26459e5e7740ef6a6cc77c76fe34'},
    'cache': {
        'enabled': True,
        'adapter': 'file',
        'version': '20160307120415',
        'path': FIXTURES_PATH
       # 'path': pj(os.path.dirname(BASE_DIR), 'tests/fixtures/snapshot.tar.gz')
    }
    # 'logger': {
    #     'path': pj(BASE_DIR, 'logs', 'tml.log')
    # }
}

