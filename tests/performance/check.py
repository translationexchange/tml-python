# encoding: UTF-8

from six.moves import range
from time import time
from tests.mock import Client
from tml import Key, Gender
from tml.translation import TranslationOption
from tml.application import Application
from tml.language import Language
from random import choice, randint
from tml.dictionary.source import SourceDictionary


class Timer(object):
    """ Timer """
    def __init__(self):
        self.start = time()
        self.times = 1

    def finish(self):
        self.stop = time()
        return self

    @property
    def time(self):
        return self.stop - self.start

    def call(self, fn, times):
        self.times = times
        for i in range(times):
            fn()
        return self.finish()

    def per_action(self):
        return self.time / self.times


def test_load_language(app):
    def load_language():
        locales = ['ru','en']
        Language.load_by_locale(app, choice(locales))
    return load_language



def main():
    c = Client.read_all()
    app = Application.load_default(c)
    t = Timer().call(test_load_language(app), 100)
    print('Load language %f' % t.per_action())
    ru = Language.load_by_locale(app, 'ru')
    dict = SourceDictionary(language = ru, source = 'index')
    t = dict.fetch(Key(label = '{actor} give you {count}',
                      description = 'somebody give you few apples',
                      language = ru))
    def translate():
        t = dict.fetch(Key(label = '{actor} give you {count}',
                      description = 'somebody give you few apples',
                      language = ru))
        actors = [{'name':'Анна','gender':'female'}, {'name':'Мария','gender':'female'}, {'name':'Вася','gender':'male'}, {'name':'Артем','gender':'male'}]
        t.execute({'count': randint(1, 1000), 'actor': choice(actors)}, {})

    t = Timer().call(translate, 1000)
    t_trans = t.time
    print 'Translate %f' % t.per_action()
    def execute():
        count = randint(1, 100)
        persons = [Gender.male('Вася'),
                   Gender.female('Маша'),
                   Gender.female('Люся'),
                   Gender.female('Кристина'),
                   Gender.male('Артем'),
                   Gender.other('Артемон'),
                   Gender.male('Коля')]
        t = TranslationOption('{name||дал, дала, дало} {to::dat} {count} яблоко', ru, {})
        t.execute({'name': choice(persons), 'to': choice(persons), 'count': count}, {})
    t = Timer().call(execute, 1000)
    print('Execute %f' % t.per_action())
    print('Total %f' % t_trans)

if __name__ == '__main__':
   main()
