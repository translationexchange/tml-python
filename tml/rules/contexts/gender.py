# encoding: UTF-8
from _ctypes import ArgumentError
from tml.strings import to_string


class Gender(object):
    """ Gender data """
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'
    def __init__(self, gender, value):
        self.value = value
        self.gender = Gender.supported_gender(gender)

    @classmethod
    def male(cls, value):
        return cls(Gender.MALE, value)

    @classmethod
    def female(cls, value):
        return cls(Gender.FEMALE, value)

    @classmethod
    def other(cls, value):
        return cls(Gender.OTHER, value)

    def __unicode__(self, *args, **kwargs):
        return to_string(self.value)

    @classmethod
    def supported_gender(cls, gender):
        """ Check is gender string is valid gender """
        if gender == Gender.MALE or gender == Gender.FEMALE or gender == Gender.OTHER:
            return gender
        raise ArgumentError('Gender unsupported: %s' % gender)

    @classmethod
    def match(cls, data):
        """ Check is object string is valid gender """
        try:
            if (type(data) is str):
                # String:
                return Gender.supported_gender(data)
            if (isinstance(data, Gender)):
                # Object is Gender instance:
                gender = data.gender
            elif (isinstance(data, dict)):
                # {'gender':'male'}
                gender = data['gender']
            elif (isinstance(data, object)):
                # check gender property:
                gender = data.gender
        except Exception as e:
            raise ArgumentError('Fault to detect gender for %s' % object, e)
        if not gender:
            raise ArgumentError('Fault to recognize gender to %s' % type(gender))
        return Gender.supported_gender(gender)


