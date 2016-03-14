# encoding: UTF-8
"""
# Copyright (c) 2015, Translation Exchange, Inc.
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
__author__ = 'a@toukmanov.ru'

from ..translation import Translation, NoneTranslation
from ..exceptions import Error
from ..utils import deprecated
from ..logger import LoggerMixin


def return_label_fallback(key):
    """ Fallaback tranlation
        Args:
            key (Key): translated key
        Returns:
            Translation
    """
    return NoneTranslation(key)


class AbstractDictionary(LoggerMixin):
    """ Dictionary """
    def __init__(self, fallback = None):
        """ Dictionary .ctor
            Args:
                fallback (function): function which generate tranlation if current is not found
        """
        self._fallback = fallback if fallback else return_label_fallback

    @deprecated
    def translate(self, key):
        """ Get key translation
            Args:
                key (Key): tranlated key
            Returns:
                Translation
        """
        return self.get_translation(key)

    def get_translation(self, key):
        """Get key translation
            Args:
                key (Key): tranlated key
            Returns:
                Translation
        """
        try:
            return self.fetch(key)
        except Exception:
            return self.fallback(key)

    def fetch(self, key):
        """ Fetch tranlation for key
            Args:
                key (translation.Key): key to translate
            Returns:
                Translation
        """
        raise NotImplementedError()

    def fallback(self, key):
        """ Key is not found """
        return self._fallback(key)

    @property
    def fallback_function(self):
        """ Fallback getter
            Returns:
                FunctionType
        """
        return self._fallback


class Hashtable(AbstractDictionary):
    """ Dictionary with translation store in hash """
    def __init__(self, fallback=None, translations=None):
        """ .ctor
            Args:
                tranlations (dict): key- tranlation code, value - tranlation options
        """
        self.translations = translations or {}
        super(Hashtable, self).__init__(fallback)

    def fetch(self, key):
        """ Tranlate key
            Args:
                key (Key): translated key
            Returns:
                Tranlation
        """
        try:
            return Translation.from_data(key, self.translations[key.key])
        except KeyError:
            pass
        raise TranslationIsNotExists(key, self)


class TranslationIsNotExists(Error):
    """ Translation for key is not found """

    def __init__(self, key, dict):
        super(TranslationIsNotExists, self).__init__()
        self.key = key
        self.dict = dict
        self._is_pending = False

    def make_pending(self):
        self._is_pending = True

    def is_pending(self):
        return self._is_pending

class TranslationIgnored(Error):
    def __init__(self, key, dict):
        super(TranslationIgnored, self).__init__()
        self.key = key
        self.dict = dict


class NoneDict(AbstractDictionary):
    """ Translate nothing """
    def fetch(self, key):
        raise TranslationIsNotExists(key, self)

