# encoding: UTF-8
from django.test import SimpleTestCase
from .translator import Translator
from gettext import ngettext
from django.template import Template
from django.template.context import Context
from django_tml import activate, use_source

class DjangoTMLTestCase(SimpleTestCase):
    """ Tests for django tml tranlator """
    def test_tranlator(self):
        t = Translator.instance()
        self.assertEquals(Translator, t.__class__, "Instance returns translator")
        self.assertEquals(t, Translator.instance(), "Singletone")

    def test_languages(self):
        """ Language switch """
        t = Translator()
        # reset en tranlation:
        en_hello_url = t.client.build_url('translation_keys/90e0ac08b178550f6513762fa892a0ca/translations',
                                          {'locale':'en', 'page': 1})
        t.client.data[en_hello_url] = {'error':'Force error'}
        self.assertEquals(['en', 'id', 'ru'], t.supported_locales)
        self.assertEquals('en', t.get_language(), 'Use default language if not set')
        self.assertEqual(u'Hello John', t.tr('Hello {name}', {'name':'John'}), 'Use fallback tranlation')
        t.activate('ru')
        self.assertEquals('ru', t.get_language(), 'Set custom language')
        self.assertEqual(u'Привет John', t.tr('Hello {name}', {'name':'John'}), 'Fetch tranlation')
        t.activate('de')
        self.assertEquals('en', t.get_language(), 'If language is not supported reset to default')
        t.activate('id')
        self.assertEquals('id', t.get_language(), 'All supported languages is works')
        t.deactivate_all()
        self.assertEquals('en', t.get_language(), 'Deactivate all')

    def test_source(self):
        """ Test languages source """
        t = Translator()
        t.activate('ru')
        t.use_source('index')
        self.assertEqual(u'Привет John', t.tr('Hello {name}', {'name':'John'}), 'Fetch translation')
        t.use_source('alpha')
        self.assertEqual(u'Hello John', t.tr('Hello {name}', {'name':'John'}), 'Use fallback translation')
        # flush missed keys on change context:
        t.use_source('index')
        self.assertEquals('sources/register_keys', t.client.url, 'Flush missed keys')
        # handle change:
        self.assertEqual(u'Привет John', t.tr('Hello {name}', {'name':'John'}), 'Fetch translation')

    def test_gettext(self):
        t = Translator()
        t.activate('ru')
        t.use_source('index')
        self.assertEqual(u'Привет %(name)s', t.ugettext('Hello {name}'), 'ugettext')
        self.assertEqual('Привет %(name)s', t.gettext('Hello {name}'), 'ugettext')
        self.assertEqual('Здорово %(name)s', t.pgettext('Greeting', 'Hi {name}'), 'ugettext')
        self.assertEquals(u'Одно яблоко', t.ungettext('One apple', '{number} apples', 1), 'ungettext + 1')
        self.assertEquals('Одно яблоко', t.ngettext('One apple', '{number} apples', 1), 'ngettext + 1')
        self.assertEquals(u'%(number)s яблоко', t.ungettext('One apple', '{number} apples', 21), 'ungettext + 21')
        self.assertEquals(u'%(number)s яблока', t.ungettext('One apple', '{number} apples', 22), 'ungettext + 22')
        self.assertEquals(u'%(number)s яблок', t.ungettext('One apple', '{number} apples', 5), 'ungettext + 5')
        self.assertEquals('%(number)s яблок', t.ngettext('One apple', '{number} apples', 12), 'ngettext + 12')

    def test_template_tags(self):
        """ Test for template tags """
        activate('ru')
        t = Template('{%load tml %}{% tr %}Hello {name}{% endtr %}')
        c = Context({'name':'John'})
        self.assertEquals(u'Привет John', t.render(c))
        t = Template(
        '''
        {%load tml %}
        {% tr trimmed %}
            Hello {name}
        {% endtr %}
        ''')
        self.assertEquals(u'''Привет John''', t.render(c).strip(), 'Trimmed support')
        t = Template(u'{%load tml %}{% tr with name="Вася" %}Hello {name}{% endtr %}')
        self.assertEquals(u'Привет Вася', t.render(c), 'With syntax')

        t = Template('{%load tml %}{% tr %}Hello {name}{% endtr %}')
        self.assertEquals(u'Привет &lt;&quot;Вася&quot;&gt;', t.render(Context({'name':'<"Вася">'})))
        t = Template(u'{%load tml %}{% tr with html|safe as name %}Hello {name}{% endtr %}')
        self.assertEquals(u'Привет <"Вася">', t.render(Context({'html':'<"Вася">'})))

    def test_blocktrans(self):
        activate('ru')
        use_source('blocktrans')
        c = Context({'name':'John'})

        t = Template('{%load tml %}{% blocktrans %}Hello {name}{% endblocktrans %}')
        self.assertEquals(u'Привет John', t.render(c))

        t = Template('{%load tml %}{% blocktrans %}Hello {{name}}{% endblocktrans %}')
        self.assertEquals(u'Привет John', t.render(c), 'Use new tranlation')
        
        t = Template('{%load tml %}{% blocktrans %}Hey {{name}}{% endblocktrans %}') 
        self.assertEquals(u'Эй John, привет John', t.render(c), 'Use old tranlation')

        t = Template('{%load tml %}{% blocktrans count count=apples_count %}One apple{% plural %}{count} apples{% endblocktrans %}')
        self.assertEquals(u'Одно яблоко', t.render(Context({'apples_count':1})),'Plural one')
        self.assertEquals(u'2 яблока', t.render(Context({'apples_count':1})),'Plural 2')
        self.assertEquals(u'21 яблоко', t.render(Context({'apples_count':21})),'Plural 21')

