# encoding: UTF-8
from __future__ import absolute_import
import unittest
import pytest
from mock import patch
from tests.mock import Client
from ...common import build_key, male, female
from tml import Application
from tml.translation import Translation
from tml.context import LanguageContext
from tml.language import Language
from tml.strings import to_string
from tml.native_decoration import get_decorator

@pytest.mark.usefixtures("init_app")
class HtmlTest(unittest.TestCase):

    def setUp(self):
        # self.client = Client()
        # self.client.read('projects/current/definition')
        # self.client.read('languages/ru')

        # self.context = self.build_context(client=self.client, locale='ru')
        # self.app = Application.load_default(self.client)
        # self.decorator = get_decorator(self.context.application)
        # self.en = self.app.language('en')
        # self.ru = self.app.language('ru')
        self.app = self.init_app()
        self.en = self.app.language('en')
        self.ru = self.app.language('ru')
        self.es = self.app.language('es')
        self.decorator = get_decorator(self.app)

    def test_decorate(self):
        key, url = build_key('{actor} give you {count} apples', language=self.en, md5='8ad5a7fe0a12729764e31a1e3ca80059')
        key2, url2 = build_key('{actor} give you {count} apples', language=self.ru, md5='8ad5a7fe0a12729764e31a1e3ca80059')

        cases = (
            (to_string('Маша любезно дала тебе 2 яблока')),
            #({'actor':[male('Вася'), ':value'],'count':1}, to_string('Вася дал тебе всего 1 яблоко, мужик!')),
        )
        for value in cases:
            actual = self.decorator.decorate(value, self.ru, self.ru, key, {'nowrap': True})
            self.assertEquals(value, value, 'render with nowrap')

        with patch.object(self.decorator, 'is_inline_mode', return_value=True):
            for value in cases:
                actual = self.decorator.decorate(value, self.ru, self.en, key, {})
                self.assertTrue(actual.startswith('<tml:label') and actual.endswith('</tml:label>'), '<tml:label/>')

                actual = self.decorator.decorate(value, self.ru, self.en, key, {'use_div':True})
                self.assertTrue(actual.startswith('<div') and actual.endswith('</div>'), '<div/>')


                actual = self.decorator.decorate(value, self.ru, self.en, key, {'use_span': True})
                self.assertTrue(actual.startswith('<span') and actual.endswith('</span>'), '<span/>')

                # locked
                actual = self.decorator.decorate(value, self.ru, self.en, key,  {'locked': True})
                self.assertTrue('tml_locked' in actual)
                #self.assertTrue(value in actual)

                # pending False
                actual = self.decorator.decorate(value, self.ru, self.en, key,  {'pending': False})
                self.assertTrue('tml_not_translated' in actual)
                #self.assertTrue(value in actual)

                # pending
                actual = self.decorator.decorate(value, self.ru, self.en, key,  {'pending': True})
                self.assertTrue('tml_pending' in actual)
                #self.assertTrue(value in actual)

                # translated
                actual = self.decorator.decorate(value, self.ru, self.en, key2, {})
                self.assertTrue('tml_translated' in actual)
                #self.assertTrue(value in actual)

                actual = self.decorator.decorate(value, self.es, self.en, key2,  {})
                self.assertTrue('tml_fallback' in actual)
                #self.assertTrue(value in actual)

    def test_decorate_element(self):
        casses = (
            (to_string('Маша'))
        )
        with patch.object(self.decorator, 'is_inline_mode', return_value=True):
            for value in casses:
                actual = self.decorator.decorate_element(value, {})
                self.assertTrue(actual.startswith('<tml:element') and actual.endswith('</tml:element>'), '<tml:element/>')

                actual = self.decorator.decorate_element(value, {'nowrap': True})
                self.assertEquals(actual, actual)

    def test_decorate_token(self):
        pass

    # def tearDown(self):
    #     self.context.deactivate()
