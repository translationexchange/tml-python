# encoding: UTF-8
import unittest
from tml.tools.list import List

class ContextStub(object):
    def tr(self, label):
        return label.upper()

class list(unittest.TestCase):
    def test_render(self):
        c = ContextStub()
        self.assertEquals('a, b, c', List(['a','b','c']).render(c), 'Just list')
        self.assertEquals('a;b;c', List(['a','b','c'], separator = ';').render(c), 'Custom separator')
        self.assertEquals('a, b AND c', List(['a','b','c'], last_separator = 'and').render(c), 'Last separator')
        self.assertEquals('a, b', List(['a','b','c'], limit = 2).render(c), 'Limit')
        self.assertEquals('a AND b', List(['a','b','c'], limit = 2, last_separator = 'and').render(c), 'Limit')
        self.assertEquals('a', List(['a'], limit = 2, last_separator = 'and').render(c), 'One element')

if __name__ == '__main__':
    unittest.main()