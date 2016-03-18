# encoding: UTF-8
"""
# Copyright (c) 2015, Translation Exchange, Inc.

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
"""
from __future__ import absolute_import
import six
import json
import unittest
import pytest
from hashlib import md5
from tml.dictionary.language import LanguageDictionary
from tml.dictionary.translations import Dictionary
from tml import initialize, tr, Gender, ContextNotConfigured, RenderEngine
import tml
from tests.mock import Client as ClientMock
from tests.mock import DummyUser
from tml import tr
from tml.dictionary.source import SourceDictionary
from tml.translation import Key
from tml.strings import to_string
from tml.session_vars import set_current_context, get_current_context


__author__ = 'a@toukamnov.ru'


import pytest
import tml
from tml.context import LanguageContext
from ..common import unittest_fixture


@pytest.mark.usefixtures("build_context")
class api_test(unittest.TestCase):
    """ Test configuration """
    def setUp(self):
        self.client = ClientMock.read_all()
        self.client.read('projects/2/translations', {'locale':'ru','page':1}, 'projects/1/translations.json')

    def test_configure_first(self):
        # tml.DEFAULT_CONTEXT = None
        set_current_context(None)
        with self.assertRaises(ContextNotConfigured):
            tr('Hello')

    def test_configure(self):
        c = self.build_context(client=self.client)
        self.assertEquals('en', c.language.locale, 'Load app defaults')
        self.assertEquals(Dictionary, type(c.dict), 'Default dictionary')
        c = self.build_context(locale='ru', key='2', client = self.client)
        self.assertEquals('ru', c.language.locale, 'Custom locale')
        self.assertEquals('2', c.language.application.key, 'Custom application id')

    def test_initialize_globals(self):
        context = self.build_context(locale='ru', application_id=None, client=self.client)
        self.assertEquals('ru', context.locale)
        self.assertEquals(1, context.application.id, 'Load default application')
        self.assertEquals(type(context.dict), Dictionary, 'No preload data')
        self.assertEquals(u'Маша любезно дала тебе 2 яблока', tr('{actor} give you {count} apples', {'actor':Gender.female('Маша'),'count':2}, 'apples'))
        self.assertEquals(u'<a href="http://site.com">Маша</a> give <strong>you</strong> 2 apples', tr('[link]{actor}[/link] give [b]you[/b] {count} apples', {'actor':Gender.female('Маша'),'count':2, 'link':{'href':'http://site.com'}}, 'apple', {'link':{'href':'http://site.com'}}))
        self.assertEquals(u'Маша give you 2 apples', tr('{user.name} give you {count} apples', {'user': DummyUser('Маша', gender='female'), 'count': 2}, 'check method'))
        self.assertEquals(u'<a href="http://site.com">Маша</a> дала <strong>тебе</strong> 1 яблоко', tr('[link]{user.name}[/link] {user|дал,дала} [b]тебе[/b] {count||яблоко,яблока}', {'user': DummyUser('Маша', gender='female'), 'count': 1, 'link': {'href': 'http://site.com'}}, 'check method token decorated'))


    def test_renderable_items(self):
        self.build_context(client = self.client)
        # hello_all = tr('Hello {name}', {'name': tml_list.List([to_string('Вася'),to_string('Петя'),'Коля'], last_separator='и')})
        # self.assertEquals(to_string('Привет Вася, Петя и Коля'), hello_all, 'Pass List instance')
        # RenderEngine.data_preprocessors.append(tml_list.preprocess_lists)
        # hello_all = tr('Hello {name}', {'name': [to_string('Вася'),to_string('Петя'),'Коля']})
        # self.assertEquals(to_string('Привет Вася, Петя, Коля'), hello_all)
        # RenderEngine.data_preprocessors.append(tml_list.ListPreprocessor)
        # hello_all = tr('Hello {name}', {'name': [to_string('Вася'),to_string('Петя'),'Коля'], 'last_separator': 'and'})
        # self.assertEquals(to_string('Привет Вася, Петя and Коля'), hello_all, 'Preprocess lists: class preprocessor')

    def test_fallback_language(self):
        label = to_string('Only english tranlation')
        c = self.build_context(client = self.client, locale = 'ru')
        key = Key(label = label, description = '', language = c.language)
        self.client.read('translation_keys/%s/translations' % key.key, {'page':1, 'locale': 'en'}, 'translation_keys/hello_en.json', True)
#        self.assertEquals('Hello (en)', c.tr(label, description = ''), 'Fallback to en')

    def test_defaults(self):
        # completly empty en translation:
        self.client.read('sources/5b7c7408d7cb048fc86170fdb3a691a8/translations',{'locale':'en'},'sources/2c1743a391305fbf367df8e4f069f9f9/translations.json',True)
        self.build_context(skip=True, source = 'empty_source', client = self.client, locale = 'ru')
        few_apples = tr('{count|apple,apples}',{'count':22})
        self.assertEquals(to_string('яблока'), few_apples, 'Use few from translation')
        self.assertEquals('apple', tr('{count|apple,apples}',{'count':1}), 'Use one from fallback')
        self.assertEquals('apples', tr('{count|apple,apples}',{'count':12}), 'Use many from fallback')

    def test_fallback_source(self):
        source = 'test_source_fallback'
        label = 'Only in English'
        # emulate empty source for ru
        source_hash = md5(source.encode('utf-8')).hexdigest()
        self.client.read('sources/%s/translations' % source_hash, {'locale':'ru'}, 'sources/sources_empty.json', True)
        # emulate source for en:
        self.client.read('sources/%s/translations' % source_hash, {'locale':'en'}, 'sources/sources_en.json', True)
        c = self.build_context(client=self.client, locale='ru', source=source, skip=True)
        self.assertEquals(label, tr(label), 'Use fallback source for en')
        c.deactivate()
        self.assertEquals(self.client.last_url, 'sources/register_keys', 'Submit missed keys url')
        expected_keys = [{"keys": [{"locale": "ru", "level": 0, "description": "", "label": "Only in English"}], "source": "test_source_fallback"}]
        submited_keys = json.loads(self.client.last_params['source_keys'])
        self.assertEquals(expected_keys, submited_keys, 'Submit missed key data')
        c = self.build_context(client = self.client, locale = 'ru', source = source)
        self.assertEquals('Never translated', tr('Never translated'), 'Never tranlated parent fallback')

    def test_fallback_rules(self):
        c = self.build_context(locale = 'ru', client = self.client)
        f = c.fallback('{count|banana:bananas}', '')
        self.assertEquals('en', f.key.language.locale, 'Fetch translation with default language')
        self.assertEquals('2 bananas', tr('{count||banana,bananas}',{'count':2}), 'Use fallback rules')

    def tearDown(self):
        self.client = None


if __name__ == '__main__':
    unittest.main()

