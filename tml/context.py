# -*- coding: utf-8 -*-
""" Context helpers for tranlation """
from .exceptions import Error

class Gender(object):
    """ Gender context """
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'

    def __init__(self, gender, value = None):
        if gender != self.MALE and gender != self.FEMALE and gender != self.OTHER:
            raise InvalidGender(gender)
        self.gender = gender
        self.value = value

    @classmethod
    def male(cls, value = None):
        return cls(Gender.MALE, value)

    @classmethod
    def female(cls, value = None):
        return cls(Gender.FEMALE, value)

class InvalidGender(Error):
    """ Error for notsupported gender """
    def __init__(self, gender):
        self.gender = gender

    def __str__(self):
        return 'Gender not supported: %s, try male|female|other'

