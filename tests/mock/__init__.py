# encoding: UTF-8

from __future__ import absolute_import
from os.path import dirname
from tml.api.mock import File

FIXTURES_PATH = '%s/fixtures' % dirname(dirname(__file__))

URLS = [('projects/current/definition', None),
        ('projects/current/definition', {'locale': 'en'}),
        ('projects/2/definition', None),
        ('languages/ru/definition', ),
        ('languages/en/definition', ),
        ('projects/1/translations', {'locale':'ru','page':1}),
        ('projects/1768/definition', {'locale':'ru,en', 'source': '/home/index'}),
        ('sources/register_keys', None),
        ('translation_keys/8ad5a7fe0a12729764e31a1e3ca80059/translations', {'locale':'ru','page':1}),
        ('translation_keys/bdc08159a02e7ff01ca188c03fa1323e/translations', {'locale':'ru','page':1}),
        ('sources/6a992d5529f459a44fee58c733255e86/translations', {'locale':'ru'}),]

class Client(File):
    def __init__(self, data = {}):
        super(Client, self).__init__(FIXTURES_PATH, data, False)

    @classmethod
    def read_all(cls):
        return cls().readdir('')


class DummyUser(object):
    def __init__(self, name, gender=None):
        self.name = name
        self.gender = gender or 'male'
