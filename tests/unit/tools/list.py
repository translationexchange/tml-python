# encoding: UTF-8
import unittest
from tml.tools.list import List
from tml.tools.template import Template
from tests.mock import Client
from tml import build_context


class ListTest(unittest.TestCase):

    def setUp(self):
        self.context = build_context(client = Client.read_all(), locale = 'ru')


    def test_render(self):
        self.assertEquals('a, b, c', List(['a','b','c']).render(self.context), 'Just list')
        self.assertEquals('a;b;c', List(['a','b','c'], separator = ';').render(self.context), 'Custom separator')
        self.assertEquals('a, b and c', List(['a','b','c'], last_separator = 'and').render(self.context), 'Last separator')
        self.assertEquals('a, b', List(['a','b','c'], limit = 2).render(self.context), 'Limit')
        self.assertEquals('a and b', List(['a','b','c'], limit = 2, last_separator = 'and').render(self.context), 'Limit')
        self.assertEquals('a', List(['a'], limit = 2, last_separator = 'and').render(self.context), 'One element')

    def test_tpl(self):
        list = List(['a','b','c'], tpl = Template('<b>{$0}</b>'))
        self.assertEquals('<b>a</b>, <b>b</b>, <b>c</b>', list.render(self.context), 'Apply template')
        list = List([{'name':'Вася','gender':'male'},{'name':'Андрей','gender':'male'},{'name':'Семен','gender':'male'}], tpl = Template('{$0::dat}'), last_separator = u'и')
        self.assertEquals(u'Васе, Андрею и Семену', list.render(self.context), 'Apply context')

if __name__ == '__main__':
    unittest.main()

