from __future__ import absolute_import
from tml_django_demo.settings import *
from tml.api.mock import File
from os.path import dirname

FIXTURES_PATH = dirname(ROOT) + '/tests/fixtures/'

def get_client():
    global FIXTURES_PATH
    return File(FIXTURES_PATH+'/').readdir('')

TML['api_client'] = get_client
TML['snapshot'] = None
TML['cache'] = None
TML['cdn'] = False
