from __future__ import absolute_import
# encoding: UTF-8
from tml.rules.contexts.gender import Gender
_viewing_user = Gender.other(None)

def reset_viewing_user():
    global _viewing_user
    _viewing_user = None

def set_viewing_user(user):
    global _viewing_user
    if user is None:
        reset_viewing_user()
    Gender.match(user)
    _viewing_user = user

def get_viewing_user(key, data = {}, context = None):
    """ Get viewing user """
    global _viewing_user
    if key == 'viewing_user':
        return _viewing_user if _viewing_user else Gender.other('')

