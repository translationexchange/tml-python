from __future__ import absolute_import
# encoding: UTF-8
import os
import shutil
import unittest
from tml.logger import Logger, LoggerNotConfigured
from ..common import FIXTURES_PATH
from codecs import open

pj = os.path.join
LANGUAGES = [{'locale':'ru'},{'locale':'en'}]

class DummyLogger(Logger):
    mode = 'w'

class ApplicationTest(unittest.TestCase):

    path = pj(FIXTURES_PATH, 'logs', 'tml.log')

    def _extract_last_line(self, path):
        with open(path, 'rb') as f:  # as binary for compat issues in py3
            f.seek(-2, 2)  # jump to the second last byte
            while f.read(1) != b'\n':  # until EOL
                f.seek(-2, 1)
            return f.readline().decode('utf-8')

    def test_init(self):
        logger = Logger(path=self.path)
        self.assertEquals(logger.path, self.path, 'logger path set')
        self.assertTrue(os.path.exists(self.path), 'path created')
        self.assertTrue(hasattr(logger, 'logger'), 'logger is set')
        self.assertEquals(Logger(path=self.path), logger, 'test singleton')

    def test_logging(self):
        logger = DummyLogger(path=self.path)
        expected_line = 'This is debug message'
        logger.debug(expected_line)
        actual_line = self._extract_last_line(self.path)
        self.assertIn(expected_line, actual_line)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(os.path.dirname(cls.path), ignore_errors=True)
        # self.assert


if __name__ == '__main__':
    unittest.main()

