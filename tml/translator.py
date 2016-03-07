# encoding: UTF-8

__author__ = 'a@toukmanov.ru, xepa4ep'

class Translator(object):
    application = None
    id = None
    name = None
    email = None
    gender = None
    mugshot = None
    link = None
    inline = None
    features = None
    image_url = None

    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def set_application(self, application):
        self.application = application

    def feature_enabled(self, key):
        if not self.features:
            return False
        return self.features.get(key, None)

    def is_inline(self):
        return self.inline == True
