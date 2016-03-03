from __future__ import absolute_import
# encoding: UTF-8
from tml.dictionary import return_label_fallback


class Fallback(object):
    def __init__(self):
        self.missed_keys = []

    def __call__(self, key):
        self.missed_keys.append(key)
        return return_label_fallback(key)

