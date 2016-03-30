# encoding: UTF-8
from __future__ import absolute_import
import unittest
import pytest
from mock import patch
from tests.mock import Client
from ..common import build_key, male, female
from tml.translation import Translation
from tml.context import LanguageContext
from tml.language import Language
from tml.strings import to_string


@pytest.mark.usefixtures("build_context")
class RenderEngineTest(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.client.read('projects/current/definition')
        self.client.read('languages/ru')
        self.context = self.build_context(client=self.client, locale='ru')
        self.russian = Language.load_by_locale(self.context.application, 'ru')

    def test_render(self):
        key, url = build_key('{actor} give you {count} apples', language=self.russian, md5='8ad5a7fe0a12729764e31a1e3ca80059')
        self.client.read(url, {'locale': 'ru'})
        t = Translation.from_data(key,
                                  self.client.get(url, params={'locale':'ru'})['results'])
        cases = (
            ({'actor': female('Маша'), 'count': 2}, to_string('Маша любезно дала тебе 2 яблока')),
            #({'actor':[male('Вася'), ':value'],'count':1}, to_string('Вася дал тебе всего 1 яблоко, мужик!')),
        )
        for input, expected in cases:
            actual = self.context.render(t, input, {'nowrap': True})
            self.assertEquals(actual, expected, 'render with nowrap')

        # with patch.object(self.context, 'is_inline_mode', return_value=True):
        #     for input, expected in cases:
        #         actual = self.context.render(t, input)
        #         self.assertTrue(actual.startswith('<tml:label') and actual.endswith('</tml:label>'), '<tml:label/>')

        #         actual = self.context.render(t, input, {'use_div': True})
        #         self.assertTrue(actual.startswith('<div') and actual.endswith('</div>'), '<div/>')

        #         actual = self.context.render(t, input, {'use_span': True})
        #         self.assertTrue(actual.startswith('<span') and actual.endswith('</span>'), '<span/>')

        #         # locked
        #         actual = self.context.render(t, input, {'locked': True})
        #         self.assertTrue('tml_locked' in actual)
        #         self.assertTrue(expected in actual)

        #         # pending False
        #         actual = self.context.render(t, input, {'pending': False})
        #         self.assertTrue('tml_not_translated' in actual)
        #         self.assertTrue(expected in actual)

        #         # pending
        #         actual = self.context.render(t, input, {'pending': True})
        #         self.assertTrue('tml_pending' in actual)
        #         self.assertTrue(expected in actual)

        #         # translated
        #         actual = self.context.render(t, input, {'locale': 'ru'})
        #         self.assertTrue('tml_translated' in actual)
        #         self.assertTrue(expected in actual)

        #         actual = self.context.render(t, input, {'locale': 'de'})
        #         self.assertTrue('tml_fallback' in actual)
        #         self.assertTrue(expected in actual)

    def tearDown(self):
        self.context.deactivate()
