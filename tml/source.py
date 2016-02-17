from dictionary.source import SourceDictionary

class SourceTranslations(object):
    """Locale => Translation dictionary per single source."""
    
    def __init__(self, source, application):
        self.source = source
        self.application = application
        self.cache = {}
        self.ignored_keys = []
        self.sources = []

    def is_ignored(self, key):
        try:
            return self.ignored_keys.index(key) and True
        except ValueError:
            return False

    def add_locale(self, locale, results=None,
                ignored_keys=None, sources=None):
        language = self.language_by_locale(locale)
        self.ignored_keys = ignored_keys or []
        self.sources = sources or []
        source_dict = SourceDictionary(self.source, language, translations=results)
        self.cache.setdefault(locale, source_dict).load_translations()
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
        return self.application.language(locale=locale)