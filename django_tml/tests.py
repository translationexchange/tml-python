# encoding: UTF-8
from django.test import SimpleTestCase
from .translator import Translator
from gettext import ngettext, gettext
from django.template import Template
from django.template.context import Context
from django_tml import activate, activate_source, inline_translations, tr,\
    deactivate_source
from tml.tools.viewing_user import set_viewing_user
from copy import copy
from django.conf import settings
from os.path import dirname
from tml.api.mock import Hashtable as DumbClient
from tml.context import SourceContext

class WithSnapshotSettings(object):
    def __init__(self):
        self.TML = {}
        for key in settings.TML:
            self.TML[key] = settings.TML[key]
        self.TML['snapshot'] = dirname(settings.BASE_DIR) + '/tests/fixtures/snapshot.tar.gz'


class DjangoTMLTestCase(SimpleTestCase):
    """ Tests for django tml tranlator """
    def setUp(self):
        Translator._instance = None # reset settings
        inline_translations.turn_off()

    def test_tranlator(self):
        t = Translator.instance()
        self.assertEquals(Translator, t.__class__, "Instance returns translator")
        self.assertEquals(t, Translator.instance(), "Singletone")

    def test_languages(self):
        """ Language switch """
        t = Translator.instance()
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
        t = Translator.instance()
        t.activate('ru')
        t.activate_source('index')
        self.assertEqual(u'Привет John', t.tr('Hello {name}', {'name':'John'}), 'Fetch translation')
        t.activate_source('alpha')
        self.assertEqual(u'Hello John', t.tr('Hello {name}', {'name':'John'}), 'Use fallback translation')
        # flush missed keys on change context:
        client = t.context.language.client
        t.activate_source('index')
        self.assertEquals('sources/register_keys', client.url, 'Flush missed keys')
        # handle change:
        self.assertEqual(u'Привет John', t.tr('Hello {name}', {'name':'John'}), 'Fetch translation')

    def test_gettext(self):
        t = Translator.instance()
        t.activate('ru')
        t.activate_source('index')
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
        activate_source('blocktrans')
        c = Context({'name':'John'})

        t = Template('{%load tml %}{% blocktrans %}Hello {name}{% endblocktrans %}')
        self.assertEquals(u'Привет John', t.render(c))

        t = Template('{%load tml %}{% blocktrans %}Hello {{name}}{% endblocktrans %}')
        self.assertEquals(u'Привет John', t.render(c), 'Use new tranlation')

        t = Template('{%load tml %}{% blocktrans %}Hey {{name}}{% endblocktrans %}') 
        self.assertEquals(u'Эй John, привет John', t.render(c), 'Use old tranlation')

        t = Template('{%load tml %}{% blocktrans count count=apples_count %}One apple{% plural %}{count} apples{% endblocktrans %}')
        self.assertEquals(u'Одно яблоко', t.render(Context({'apples_count':1})),'Plural one')
        self.assertEquals(u'2 яблока', t.render(Context({'apples_count':2})),'Plural 2')
        self.assertEquals(u'21 яблоко', t.render(Context({'apples_count':21})),'Plural 21')

    def test_inline(self):
        """ Inline tranlations wrapper """
        activate('ru')
        inline_translations.turn_on()
        c = Context({'name':'John'})
        t = Template(u'{%load tml %}{% tr %}Hello {name}{% endtr %}')

        self.assertEquals(u'<tml:label class="tml_translatable tml_translated" data-translation_key="90e0ac08b178550f6513762fa892a0ca" data-target_locale="ru">Привет John</tml:label>',
                          t.render(c),
                          'Wrap translation')
        t = Template(u'{%load tml %}{% tr nowrap %}Hello {name}{% endtr %}')
        self.assertEquals(u'Привет John',
                          t.render(c),
                          'Nowrap option')

        t = Template(u'{%load tml %}{% blocktrans %}Hello {name}{% endblocktrans %}')
        self.assertEquals(u'Привет John',
                          t.render(c),
                          'Nowrap blocktrans')

        t = Template(u'{%load tml %}{% tr %}Untranslated{% endtr %}')
        self.assertEquals(u'<tml:label class="tml_translatable tml_not_translated" data-translation_key="9bf6a924c9f25e53a6b07fc86783bb7d" data-target_locale="ru">Untranslated</tml:label>',
                          t.render(c),
                          'Untranslated')
        activate('ru')
        inline_translations.turn_off()
        t = Template(u'{%load tml %}{% tr %}Hello {name}{% endtr %}')
        t = Template(u'{%load tml %}{% blocktrans %}Hello {name}{% endblocktrans %}')
        self.assertEquals(u'Привет John',
                          t.render(c),
                          'Turn off inline')

    def test_sources_stack(self):
        t = Translator.instance()
        self.assertEqual(None, t.source, 'None source by default')
        t.activate_source('index')
        self.assertEqual('index', t.source, 'Use source')
        t.enter_source('auth')
        self.assertEqual('auth', t.source, 'Enter (1 level)')
        t.enter_source('mail')
        self.assertEqual('mail', t.source, 'Enter (2 level)')
        t.exit_source()
        self.assertEqual('auth', t.source, 'Exit (2 level)')
        t.exit_source()
        self.assertEqual('index', t.source, 'Exit (1 level)')
        t.exit_source()
        self.assertEqual(None, t.source, 'None source by default')

        t.activate_source('index')
        t.enter_source('auth')
        t.enter_source('mail')
        t.activate_source('inner')
        t.exit_source()
        self.assertEqual(None, t.source, 'Use destroys all sources stack')

    def test_preprocess_data(self):
        activate('ru')
        self.assertEquals(u'Привет Вася and Петя', tr('Hello {name}', {'name':['Вася','Петя']}))
        t = Template(u'{%load tml %}{% tr %}Hello {name}{% endtr %}')
        self.assertEquals(u'Привет Вася and Петя', t.render(Context({'name':['Вася','Петя']})))

    def test_viewing_user(self):
        activate('ru')
        set_viewing_user({'name':'John','gender':'male'})
        deactivate_source()
        self.assertEquals('Mr', tr('honorific'))
        set_viewing_user('female')
        self.assertEquals('Ms', tr('honorific'))

    def test_snapshot_context(self):
        t = Translator(WithSnapshotSettings())
        self.assertTrue(t.use_snapshot, 'Use snapshot with settings')
        t.activate('ru')
        self.assertEquals('Test', t.context.tr('Test'), 'Stub translation without source')
        t.activate_source('xxxx')
        self.assertEquals(u'Тест', t.context.tr('Test'), 'Works with source')
        t.activate_source('notexists')
        self.assertEquals(u'Test', t.context.tr('Test'), 'Notexists source')

