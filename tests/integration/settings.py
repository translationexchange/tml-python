import os
pj = os.path.join

TML = {
    'environment': 'test',
    'application': {'key': 'e76ba38d2ba022d1095217cfa5d1832b5c7216fff87c5b62bdcc5c73534e316f'},
    'cache': {
        'enabled': True,
        'adapter': 'file',
        'version': '20160303075532',
        'path': pj(BASE_DIR, 'tml/cache')
       # 'path': pj(os.path.dirname(BASE_DIR), 'tests/fixtures/snapshot.tar.gz')
    },
    'agent': {
        'enabled': True,
        'type':    'agent',
        'cache':   86400  # timeout every 24 hours
    },
    'data_preprocessors': ('tml.tools.list.preprocess_lists',),
    'env_generators': ('tml.tools.viewing_user.get_viewing_user',),
    'logger': {
        'path': pj(BASE_DIR, 'logs', 'tml.log')
    }
}

