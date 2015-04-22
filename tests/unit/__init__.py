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

from tml.dictionary.language import LanguageDictionary
from tml.dictionary.translations import Dictionary
from tml import configure, tr, build_context, Gender, ContextNotConfigured, RenderEngine
import tml
from tests.mock import Client as ClientMock
import unittest
from tml.dictionary.source import SourceDictionary
from tml.tools import list as tml_list
from tml.translation import Key
from hashlib import md5

__author__ = 'a@toukamnov.ru'


class api_test(unittest.TestCase):
    """ Test configuration """
    def setUp(self):
        self.client = ClientMock.read_all()
        self.client.read('applications/2/translations', {'locale':'ru','page':1}, 'applications/1/translations.json')

    def test_configure_first(self):
        tml.DEFAULT_CONTEXT = None
        with self.assertRaises(ContextNotConfigured):
            tr('Hello')

    def test_configure(self):
        c = build_context(client = self.client)

        self.assertEquals('en', c.language.locale, 'Load app defaults')
        self.assertEquals(Dictionary, type(c.dict), 'Default dictionary')

        c = build_context(locale = 'ru', application_id = 2, client = self.client)
        self.assertEquals('ru', c.language.locale, 'Custom locale')
        self.assertEquals(2, c.language.application.id, 'Custom application id')


#    def test_configure_globals(self):
#        configure(locale = 'ru', application_id = None, client = self.client)
#        self.assertEquals('ru', tml.DEFAULT_CONTEXT.locale)
#        self.assertEquals(1, tml.DEFAULT_CONTEXT.application.id, 'Load default application')
#        self.assertEquals(type(tml.DEFAULT_CONTEXT.dict), Dictionary, 'No preload data')
#        self.assertEquals(u'Маша любезно дала тебе 2 яблока', tr('{actor} give you {count} apples', {'actor':Gender.female('Маша'),'count':2}, 'apples'))
#        self.assertEquals(u'<a href="http://site.com">Маша</a> give <strong>you</strong> 2 apples', tr('[link]{actor}[/link] give [b]you[/b] {count} apples', {'actor':Gender.female('Маша'),'count':2}, 'apple', {'link':{'href':'http://site.com'}}))

    def test_renderable_items(self):
        c = build_context(client = self.client)
        hello_all = c.tr('Hello {name}', {'name': tml_list.List([u'Вася',u'Петя','Коля'], last_separator='и')})
        self.assertEquals(u'Привет Вася, Петя и Коля', hello_all, 'Pass List instance')
        RenderEngine.data_preprocessors.append(tml_list.preprocess_lists)
        hello_all = c.tr('Hello {name}', {'name': [u'Вася',u'Петя','Коля']})
        self.assertEquals(u'Привет Вася, Петя and Коля', hello_all, 'Preprocess lists')

    def test_fallback_language(self):
        label = u'Only english tranlation'
        c = build_context(client = self.client, locale = 'ru')
        key = Key(label = label, description = '', language = c.language)
        self.client.read('translation_keys/%s/translations' % key.key, {'page':1, 'locale': 'en'}, 'translation_keys/hello_en.json', True)
        self.assertEquals('Hello (en)', c.tr(label, description = ''), 'Fallback to en')

    def test_fallback_source(self):
        source = 'test_source_fallback'
        label = 'Only in English'
        # emulate empty source for ru
        source_hash = md5(source).hexdigest()
        self.client.read('sources/%s/translations' % source_hash, {'locale':'ru'}, 'sources/sources_empty.json', True)
        # emulate source for en:
        self.client.read('sources/%s/translations' % source_hash, {'locale':'en'}, 'sources/sources_en.json', True)
        c = build_context(client = self.client, locale = 'ru', source = source)
        self.assertEquals('Has english translation', c.tr(label),'Use fallback source for en')
        del c
        self.assertEquals(self.client.url, 'sources/register_keys', 'Submit missed keys url')
        self.assertEquals({'source_keys': '[{"keys": [{"locale": "ru", "level": 0, "description": "", "label": "Only in English"}], "source": "test_source_fallback"}]'}, self.client.params, 'Submit missed key data')
        c = build_context(client = self.client, locale = 'ru', source = source)
        self.assertEquals('Never translated', c.tr('Never translated'), 'Never tranlated parent fallback')

    def test_fallback_rules(self):
        c = build_context(locale = 'ru', client = self.client)
        f = c.fallback('{count|banana:bananas}', '')
        self.assertEquals('en', f.key.language.locale, 'Fetch translation with default language')
        self.assertEquals('2 bananas', c.tr('{count||banana,bananas}',{'count':2}), 'Use fallback rules')

    def test_defaults(self):
        # completly empty en translation:
        self.client.read('sources/5b7c7408d7cb048fc86170fdb3a691a8/translations',{'locale':'en'},'sources/2c1743a391305fbf367df8e4f069f9f9/translations.json',True)
        c = build_context(source = 'empty_source', client = self.client, locale = 'ru')
        self.assertEquals('яблока', c.tr('{count|apple,apples}',{'count':22}), 'Use few from translation')
        self.assertEquals('apple', c.tr('{count|apple,apples}',{'count':1}), 'Use one from fallback')
        self.assertEquals('apples', c.tr('{count|apple,apples}',{'count':12}), 'Use many from fallback')


if __name__ == '__main__':
    unittest.main()

