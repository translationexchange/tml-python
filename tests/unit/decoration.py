from __future__ import absolute_import
# encoding: UTF-8
import unittest
from tml.decoration import Text, Tag, Set, TagFactory, UnsupportedTag,\
    AttributeIsNotSet
from tml.decoration.parser import parse, ParseError

class DecorationTest(unittest.TestCase):

    def setUp(self):
        self.a_html = '<a href="http://translationexchange.com/">text</a>'
        self.a_body = 'text'
        self.attrs = {'link':{'href':'http://translationexchange.com/'}}
 
    def test_text(self):
        t = Text('Hello')
        self.assertEquals('Hello', t.render(), 'Render text')
        t = t.append(' ').append('world')
        self.assertEquals('Hello world', t.render(), 'Append')

    def test_set(self):
        s = Set()
        s.append('Hello').append(Text(' ')).append(Text('world'))
        self.assertEquals('Hello world', s.render())
        s2 = Set()
        s2.append('Print "').append(s).append(Text('"!'))
        self.assertEquals('Print "Hello world"!', s2.render(), 'Nested set')

    def test_attrs(self):
        a = Tag('link', 'a', ['href']).append(self.a_body)
        self.assertEquals(self.a_html, a.render(self.attrs), 'Render with attrs')
        b = Tag('b', 'strong').append('bold: ').append(a)
        self.assertEquals('<strong>bold: %s</strong>' % self.a_html, b.render(self.attrs), 'Render with attrs')
        with self.assertRaises(AttributeIsNotSet):
            a.render()

    def test_tag(self):
        t = Tag('link', 'a', ['href',])
        t.append(Text('click me'))
        t.append(' please')
        t_html = '<a href="http://translationexchange.com/">click me please</a>'
        self.assertEquals(t_html, t.render(self.attrs))
        t2 = Tag('b', 'b')
        t2.append(Text('Read and ')).append(t)
        self.assertEquals('<b>Read and '+t_html+'</b>', t2.render(self.attrs), 'Inner tag')

    def test_factory(self):
        tf = TagFactory().allow('link', 'a', ['href'])
        a = tf.build('link').append(self.a_body)
        self.assertEquals(self.a_html, a.render(self.attrs), 'Intance data with TF')
        tf.allow('b', 'strong')
        b = tf.build('b').append('Bold ').append(a)
        self.assertEquals('<strong>Bold %s</strong>' % self.a_html, b.render(self.attrs), 'Instance b')
        with self.assertRaises(UnsupportedTag):
            tf.build('zzz')

    def test_simple(self):
        self.assertEquals('hello <strong>world</strong>!', parse('hello [b:world]!').render())
        self.assertEquals('hello <strong>world</strong>!', parse('hello [b]world[/b]!').render())#
        self.assertEquals('hello <strong>world</strong>:', parse('hello [b]world[/b]:').render(), 'special symbols `:`')
        self.assertEquals('hello <strong>world</strong>/', parse('hello [b]world[/b]/').render(), 'special symbols `\`')
        self.assertEquals('hello <strong>world</strong>[]', parse('hello [b]world[/b][]').render(), 'special symbols `[]`')

    def test_embed(self):
        expected = 'say <i>hello <strong>world</strong></i>!'
        self.assertEquals(expected, parse('say [i]hello [b:world][/i]!').render(),'[i][b:][/i]')
        self.assertEquals(expected, parse('say [i:hello [b:world]]!').render(),'[i:[b:]]')
        self.assertEquals(expected, parse('say [i:hello [b]world[/b]]!').render(),'[i:[b][/b]]')
        self.assertEquals('<a href="http://translationexchange.com/">%s</a>' % expected, parse('[link: say [i:hello [b]world[/b]]!]').render(self.attrs),'[link: [i: [b][/b]]]')

    def test_parsing_errors(self):
        with self.assertRaises(ParseError) as context:
            parse('?[/b]')
            self.assertEquals(1, context.exception.pos)
        with self.assertRaises(ParseError) as context:
            parse('![hello]baby[/hello]')
            self.assertEquals(1, context.exception.pos)
        with self.assertRaises(ParseError) as context:
            parse('![i]baby[/b]')
            self.assertEquals(8, context.exception.pos)
        with self.assertRaises(ParseError) as context:
            parse('[b]not closed')
        with self.assertRaises(ParseError) as context:
            parse('[b:not closed')
        with self.assertRaises(ParseError) as context:
            parse('[b:not [/b]')

    def test_self_closed(self):
        self.assertEquals('Hello<br/>world', parse('Hello[br]world').render(), 'br')
        self.assertEquals('<h1>Hello<br/>world</h1>', parse('[h1]Hello[br]world[/h1]').render(), 'h1: br')
        self.assertEquals('<h1>Hello<br/>world</h1>', parse('[h1: Hello[br]world]').render(), 'h1: br')


if __name__ == '__main__':
    unittest.main()

