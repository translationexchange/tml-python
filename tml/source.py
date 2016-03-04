from .dictionary.source import SourceDictionary

class SourceTranslations(object):
    """Locale => Translation dictionary per single source."""

    def __init__(self, source, application):
        self.source = source
        self.application = application
        self.cache = {}
        self.ignored_keys = set([])

    def is_ignored(self, key):
        return key in self.ignored_keys

    def add_locale(self, locale, results=None,
                ignored_keys=None, sources=None, **init_kwargs):
        language = self.language_by_locale(locale)
        self.ignored_keys |= set(ignored_keys or [])
        if locale in self.cache:
            self.cache[locale].load_translations()
        else:
            self.cache[locale] = SourceDictionary(self.source, language, translations=results, **init_kwargs).load_translations()
        return self

    def hashtable_by_locale(self, locale):
        return self.cache.get(locale, None)

    def cached_translation(self, locale, key):
        """ .ctor
        Args:
            locale (string): locale name
            key (string): translation key
        Returns:
            translation.Translation object

        """
        locale_dict = self.cache.get(locale)
        return locale_dict.fetch(key)

    def language_by_locale(self, locale):
        if not self.application:
            raise Exception("Application is not configured yet")

        return self.application.language(locale=locale, fallback_to_dummy=False)
