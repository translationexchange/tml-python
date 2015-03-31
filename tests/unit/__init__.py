# encoding: UTF-8
#--
# Copyright (c) 2015, Translation Exchange, Inc.
#
#  _______                  _       _   _             ______          _
# |__   __|                | |     | | (_)           |  ____|        | |
#    | |_ __ __ _ _ __  ___| | __ _| |_ _  ___  _ __ | |__  __  _____| |__   __ _ _ __   __ _  ___
#    | | '__/ _` | '_ \/ __| |/ _` | __| |/ _ \| '_ \|  __| \ \/ / __| '_ \ / _` | '_ \ / _` |/ _ \
#    | | | | (_| | | | \__ \ | (_| | |_| | (_) | | | | |____ >  < (__| | | | (_| | | | | (_| |  __/
#    |_|_|  \__,_|_| |_|___/_|\__,_|\__|_|\___/|_| |_|______/_/\_\___|_| |_|\__,_|_| |_|\__, |\___|
#                                                                                        __/ |
#                                                                                       |___/
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#++
from tml.dictionary.language import LanguageDictionary
from tml.dictionary.translations import Dictionary
from tml import configure, tr, context, Context, Gender, ContextNotConfigured, submit_missed
import tml
from tests.mock import Client as ClientMock
import unittest
from tml.dictionary.source import SourceDictionary
from tml.tools import list as tml_list

__author__ = 'a@toukamnov.ru'


class api_test(unittest.TestCase):
    """ Test configuration """
    def setUp(self):
        self.client = ClientMock.read_all()
        self.client.read('applications/2/translations', {'locale':'ru','page':1}, 'applications/1/translations.json')

    def test_configure_first(self):
        tml.context = Context() # reset context
        with self.assertRaises(ContextNotConfigured):
            tr('Hello')
        with self.assertRaises(ContextNotConfigured):
            submit_missed()

    def test_configure(self):
        c = Context()
        c.configure(None, client = self.client)

        self.assertEquals('en', c.language.locale, 'Load app defaults')
        self.assertEquals(Dictionary, type(c.dict), 'Default dictionary')

        c.configure(None, locale = 'ru', application_id = 2, client = self.client)
        self.assertEquals('ru', c.language.locale, 'Custom locale')
        self.assertEquals(2, c.language.application.id, 'Custom application id')


    def test_configure_globals(self):
        configure(token = None, locale = 'ru', application_id = None, client = self.client)
        self.assertEquals('ru', tml.context.locale)
        self.assertEquals(1, tml.context.language.application.id, 'Load default application')
        self.assertEquals(type(tml.context.dict), Dictionary, 'No preload data')
        self.assertEquals(u'Маша любезно дала тебе 2 яблока', tr('{actor} give you {count} apples', {'actor':Gender.female('Маша'),'count':2}, 'apples'))
        self.assertEquals(u'<a href="http://site.com">Маша</a> give <strong>you</strong> 2 apples', tr('[link]{actor}[/link] give [b]you[/b] {count} apples', {'actor':Gender.female('Маша'),'count':2}, 'apple', {'link':{'href':'http://site.com'}}))

    def test_renderable_items(self):
        c = Context(client = self.client)
        hello_all = c.tr('Hello {name}', {'name': tml_list.List([u'Вася',u'Петя','Коля'], last_separator='и')})
        self.assertEquals(u'Привет Вася, Петя и Коля', hello_all, 'Pass List instance')
        Context.data_preprocessors.append(tml_list.preprocess_lists)
        hello_all = c.tr('Hello {name}', {'name': [u'Вася',u'Петя','Коля']})
        self.assertEquals(u'Привет Вася, Петя and Коля', hello_all, 'Preprocess lists')


if __name__ == '__main__':
    unittest.main()

