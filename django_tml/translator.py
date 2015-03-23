# encoding: UTF-8
from django.conf import settings
from django.utils.translation.trans_real import to_locale, templatize, deactivate_all, parse_accept_lang_header, language_code_re, language_code_prefix_re, _BROWSERS_DEPRECATED_LOCALES 
from tml import Context
from tml.application import LanguageNotSupported, Application
from django_tml.cache import CachedClient
from tml import Key
from tml.translation import TranslationOption
from django.utils.translation import LANGUAGE_SESSION_KEY
from tml.legacy import text_to_sprintf, suggest_label
from types import FunctionType


def to_str(fn):
    def tmp(*args, **kwargs):
        return fn(*args, **kwargs).encode('utf-8')
    return tmp

def fallback_locale(locale):
    exploded = locale.split('-')
    if 2==len(exploded):
        return exploded[0]
    else:
        return None


class Translator(object):
    """ Basic tranlator class """
    _instance = None

    @classmethod
    def instance(cls):
        """ Singletone
            Returns:
                Translator
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.locale = None
        self.source = None
        self._context = None
        self._supported_locales = None
        self._client = None


    def build_context(self):
        """ Build context instance for locale
            Args:
                locale (str): locale name (en, ru)
            Returns:
                Context
        """
        return Context(locale = self.locale,
                       source = self.source,
                       client = self.client)

    @property
    def client(self):
        """ API client property (overrided in unit-tests)
            Returns:
                Client
        """
        if self._client is None:
            self._client = self.build_client()
        return self._client

    def build_client(self):
        if 'api_client' in settings.TML:
            # Custom client:
            custom_client = settings.TML['api_client']
            if type(custom_client) is FunctionType:
                # factory function:
                return custom_client()
            elif custom_client is str:
                # full factory function or class name: path.to.module.function_name
                custom_client_import = '.'.split(custom_client)
                module = __import__('.'.join(custom_client[0, -1]))
                return getattr(module, custom_client[-1])()
            elif custom_client is object:
                # custom client as is:
                return custom_client
        return CachedClient.instance()

    @property
    def context(self):
        """ Current context cached property
            Returns:
                Context
        """
        if self._context is None:
            try:
                self._context = self.build_context()
            except LanguageNotSupported:
                # Activated language is not supported:
                self.locale = None # reset locale
                self._context = self.build_context()
        return self._context


    def get_language(self):
        """ getter to current language """
        return self.context.language.locale

    def activate(self, locale):
        """ Activate selected language 
            Args:
                locale (string): selected locale
        """
        self.locale = locale
        self.reset_context()

    def use_source(self, source):
        """ Get source
            Args:
                source (string): source code
        """
        self.source = source
        self.reset_context()
        return self

    def reset_context(self):
        self._context = None

    def deactivate(self):
        """ Use default locole """
        self.locale = None
        self.reset_context()

    def gettext_noop(self, message):
        return message

    @to_str
    def gettext(self, message):
        return self.ugettext(message)

    @to_str
    def ngettext(self, singular, plural, number):
        return self.ungettext(singular, plural, number)

    def ugettext(self, message):
        return self.translate(message)

    def ungettext(self, singular, plural, number):
        if number == 1:
            return self.translate(singular, {'number': number})
        else:
            return self.translate(plural, {'number': number})

    @to_str
    def pgettext(self, context, message):
        return self.translate(message, description = context)

    @to_str
    def npgettext(self, context, singular, plural, number):
        if number == 1:
            return self.translate(singular, {'number': number}, context)
        else:
            return self.translate(plural, {'number': number}, context)

    def translate(self, label, data = {}, description = None):
        key = Key(label = suggest_label(label), description= description, language = self.context.language)
        translation = self.context.dict.translate(key)
        ret = text_to_sprintf(translation.fetch_option(data, {}).label, self.context.language)
        return ret


    def get_language_bidi(self):
        return self.context.language.right_to_left

    def check_for_language(self, lang_code):
        """ Check is language supported by application
            Args:
                string lang_code
            Returns:
                boolean
        """
        return lang_code in self.supported_locales

    @property
    def supported_locales(self):
        if self._supported_locales is None:
            self._supported_locales = [str(locale) for locale in Application.load_default(self.client).supported_locales]
        return self._supported_locales


    def to_locale(self, language):
        return to_locale(language)

    def get_language_from_request(self, request, check_path=False):
        """
        Analyzes the request to find what language the user wants the system to
        show. Only languages listed in settings.LANGUAGES are taken into account.
        If the user requests a sublanguage where we have a main language, we send
        out the main language.
    
        If check_path is True, the URL path prefix will be checked for a language
        code, otherwise this is skipped for backwards compatibility.
        """
        if check_path:
            lang_code = self.get_language_from_path(request.path_info)
            if lang_code is not None:
                return lang_code
    
        if hasattr(request, 'session'):
            # for backwards compatibility django_language is also checked (remove in 1.8)
            lang_code = request.session.get(LANGUAGE_SESSION_KEY, request.session.get('django_language'))
            if self.check_for_language(lang_code):
                return lang_code
    
        lang_code = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if self.check_for_language(lang_code):
            return lang_code
    
        accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        for accept_lang, unused in parse_accept_lang_header(accept):
            if accept_lang == '*':
                break
            if not language_code_re.search(accept_lang):
                continue
            if self.check_for_language(accept_lang):
                return accept_lang

        return self.context.application.default_locale

    def get_language_from_path(self, path, strict=False):
        """
        Returns the language-code if there is a valid language-code
        found in the `path`.
    
        If `strict` is False (the default), the function will look for an alternative
        country-specific variant when the currently checked is not found.
        """
        regex_match = language_code_prefix_re.match(path)
        if not regex_match:
            return None
        lang_code = regex_match.group(1)
        try:
            return self.get_supported_language_variant(lang_code, strict=strict)
        except LookupError:
            return None


    def get_supported_language_variant(self, lang_code, strict=False):
        """
        Returns the language-code that's listed in supported languages, possibly
        selecting a more generic variant. Raises LookupError if nothing found.
    
        If `strict` is False (the default), the function will look for an alternative
        country-specific variant when the currently checked is not found.
    
        lru_cache should have a maxsize to prevent from memory exhaustion attacks,
        as the provided language codes are taken from the HTTP request. See also
        <https://www.djangoproject.com/weblog/2007/oct/26/security-fix/>.
        """
        _supported = self.context.application.supported_locales
        if lang_code:
            # some browsers use deprecated language codes -- #18419
            replacement = _BROWSERS_DEPRECATED_LOCALES.get(lang_code)
            if lang_code not in _supported and replacement in _supported:
                return replacement
            # if fr-ca is not supported, try fr.
            generic_lang_code = lang_code.split('-')[0]
            for code in (lang_code, generic_lang_code):
                if self.check_for_language(code):
                    return code
            if not strict:
                # if fr-fr is not supported, try fr-ca.
                for supported_code in _supported:
                    if supported_code.startswith(generic_lang_code + '-'):
                        return supported_code
        raise LookupError(lang_code)

    def templatize(self, src, origin=None):
        return templatize(src, origin)

    def deactivate_all(self):
        self.locale = None
        self.reset_context()

    def tr(self, label, data = {}, description = '', options = {}):
        try:
            return self.context.tr(label, data, description, options)
        except settings.TML.get('handle', Exception) as e:
            # Use label if tranlation fault:
            return TranslationOption(label = label, language= self.context.language).execute(data, options)

