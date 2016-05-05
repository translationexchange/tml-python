import unittest
import pytest
import glob
import re
from codecs import open
from tests.common import FakeUser
from tml.tokenizers.dom import DomTokenizer
from tml.token.transform import PIPE_CHAR
from tml import get_current_context
from tml.utils import to_string
from tests.mock import FIXTURES_PATH


@pytest.mark.usefixtures("build_context")
class DomTokenizerTest(unittest.TestCase):

    def setUp(self):
        self.app = self.build_context()

    def test_initialize(self):
        dt = DomTokenizer({}, {
                          'debug': True
                          })

        translated = dt.translate("<html><body><h1>Mr. Belvedere Fan Club</h1></body></html>")
        self.assertEquals(translated, to_string("<h1>{{{Mr. Belvedere Fan Club}}}</h1>"))

        translated = dt.translate("<p>Mr. Belvedere Fan Club</p>")
        self.assertEquals(translated, to_string("<p>{{{Mr. Belvedere Fan Club}}}</p>"))

        translated = dt.translate("<h1>Mr. Belvedere Fan Club</h1>")
        self.assertEquals(translated, to_string("<h1>{{{Mr. Belvedere Fan Club}}}</h1>"))

        # translated = dt.translate("<p><a class='the-link' href='https://github.com/tmpvar/jsdom'>jsdom's Homepage</a></p>")
        # self.assertEquals(translated, "<p><a class='the-link' href='https://github.com/tmpvar/jsdom'>{{{jsdom's Homepage}}}</a></p>")

        # for file in glob.glob(FIXTURES_PATH + '/dom/**/*.html'):
        #     original = open(file, encoding='utf-8').read().splitlines()
        #     result = open(re.sub('html$', 'tml', file), encoding='utf-8').read().splitlines()

        #     to_translate = "".join(original)
        #     translated = dt.translate(to_translate.rstrip())

        #     translated_new = "".join(translated)

        #     result_new = ""
        #     for line in result:
        #         result_new += line.rstrip()
        #     self.assertEquals(translated, result_new)
