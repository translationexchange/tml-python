from __future__ import absolute_import
# encoding: UTF-8
import unittest
from tml.tools.list import List
from tml.tools.template import Template
from tests.mock import Client
from tml import build_context
from tml.strings import to_string

class ListTest(unittest.TestCase):

    def setUp(self):
        self.context = build_context(client=Client.read_all(), locale='ru')

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
        list = List([{'name':to_string('Вася'),'gender':'male'},{'name':to_string('Андрей'),'gender':'male'},{'name':to_string('Анна'),'gender':'female'}], tpl = Template('{$0::dat}'), last_separator = to_string('и'))
        self.assertEquals(to_string('Васе, Андрею и Анне'), list.render(self.context))
        list = List([{'name':to_string('Вася'),'gender':'male'},{'name':to_string('Андрей'),'gender':'male'},{'name':to_string('Анна'),'gender':'female'}], tpl='{$0::dat}', last_separator=to_string('и'))
        self.assertEquals(to_string('Васе, Андрею и Анне'), list.render(self.context))

if __name__ == '__main__':
    unittest.main()

