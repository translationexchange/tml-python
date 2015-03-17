# encoding: UTF-8
from django.conf import settings
from django.utils import translation
from django.utils.translation.trans_real import to_locale, get_language_from_request, get_language_from_path, _supported, templatize, deactivate_all 
from tml import Context
from collections import OrderedDict
from tml.application import LanguageNotSupported


def to_str(fn):
    def tmp(*args, **kwargs):
        return fn(*args, **kwargs).encode('utf-8')
    return tmp 


class Tranlator(object):
    """ Basic tranlator class """
    def __init__(self):
        self.contexts = {}
        self.default = self.build_context(None)
        self.context = self.default

    def build_context(self, locale):
        """ Build context instance for locale
            Args:
                locale (str): locale name (en, ru)
            Returns:
                Context
        """
	ret = Context()
	try:
    	    ret.configure(token = settings.TML.get('token', None), locale = locale)
	except LanguageNotSupported:
	    ret.configure(token = settings.TML.get('token', None), locale = None)
	return ret

    def get_language(self):
        """ getter to current language """
        if self.context:
            return self.context.language.locale
        else:
            return settings.LANGUAGE_CODE

    def activate(self, language):
        """ Activate selected language """
        if not language in self.contexts:
            self.contexts[language] = self.build_context(language)
        self.context = self.contexts[language]
	print self.context

    def deactivate(self):
        self.context = self.default


    def gettext_noop(self, message):
        return message

    @to_str
    def gettext(self, message):
        return self.ugettext()

    @to_str
    def ngettext(self, singular, plural, number):
        return self.ungettext(singular, plural, number)

    def ugettext(self, message):
	print self.context.language.locale
        return self.context.tr(message)

    def ungettext(self, singular, plural, number):
        if number == 1:
            return self.context.tr(singular, {'number': number})
        else:
            return self.context.tr(plural, {'number': number})

    @to_str
    def pgettext(self, context, message):
        return self.tr(message, description = context)

    @to_str
    def npgettext(self, context, singular, plural, number):
        if number == 1:
            return self.tr(singular, {'number': number}, context)
        else:
            return self.tr(plural, {'number': number}, context)


    def get_language_bidi(self):
        return self.context.language.right_to_left

    def check_for_language(self, lang_code):
        try:
            return True if not self.context.language.application.get_language_url(lang_code) is None else False
        except Exception:
            return False

    def to_locale(self, language):
        return to_locale(language)

    def get_language_from_request(self, request, check_path=False):
        return get_language_from_request(request, check_path)
    
    
    def get_language_from_path(self, path):
        return get_language_from_path(path)

    def templatize(self, src, origin=None):
        return templatize(src, origin)
    
    
    def deactivate_all(self):
        return deactivate_all()

if settings.TML.get('monkeypatch', False):
    translation._trans = Tranlator()
    _supported = OrderedDict

