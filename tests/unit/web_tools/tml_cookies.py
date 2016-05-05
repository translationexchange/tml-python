from __future__ import absolute_import
# encoding: UTF-8
import pytest
import os
import time
import unittest
from tml.web_tools.tml_cookies import BaseTmlCookieHandler


@pytest.mark.usefixtures("init_app")
class TmlCookiesTest(unittest.TestCase):

    def setUp(self):
        self.app = self.init_app()
        self.en = self.app.language('en')
        self.ru = self.app.language('ru')
        self.client = self.app.client
        self.application_key = "123"

    def test_cookies(self):
        self.cookies = BaseTmlCookieHandler(None, self.application_key)
        self.assertIsInstance(self.cookies, BaseTmlCookieHandler)
        self.assertEqual(self.cookies.tml_cookie, {})

