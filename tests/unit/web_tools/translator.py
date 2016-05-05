import pytest
import os
import time
import unittest
from tml import get_current_context
from tml.api.client import Client
from tml.web_tools.translator import BaseTranslation
from tml.context import SourceContext
from tml.config import Config


@pytest.mark.usefixtures("init_app")
class TranslatorTest(unittest.TestCase):

    def setUp(self):
        self.app = self.init_app()
        self.en = self.app.language('en')
        self.ru = self.app.language('ru')
        self.client = self.app.client

    def test_translation(self):
        self.translation = BaseTranslation({})
        self.config = Config()
        self.assertIsInstance(self.translation, BaseTranslation)
        self.assertIsInstance(BaseTranslation.instance(), BaseTranslation)
        self.assertIsInstance(self.translation.build_context(), SourceContext)
        self.assertEquals(self.translation.context, get_current_context())
        self.assertEquals(self.translation.application, get_current_context().application)
        self.assertEquals(self.translation.application_key, self.config.application_key())
        self.assertEquals(self.translation.languages, get_current_context().application.languages)
        self.assertIsInstance(self.translation.build_client(), Client)
        self.assertEquals(self.translation.client, get_current_context().client)



if  __name__ == '__main__':
    unittest.main()
