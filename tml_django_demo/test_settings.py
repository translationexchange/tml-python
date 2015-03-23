from tml_django_demo.settings import *
from tml.api.mock import File
from os.path import dirname

def get_client():
    return File(dirname(BASE_DIR) + '/tests/fixtures/').readdir('')

TML['api_client'] = get_client

