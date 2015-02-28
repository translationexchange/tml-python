# -*- coding: utf-8 -*-

class Error(Exception):
    """ Base TML exception """
    pass


class RequiredArgumentIsNotPassed(Error):
    def __init__(self, key, data):
        self.key = key
        self.data = data

