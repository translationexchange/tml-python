from threading import local

_threadlocals = local()


def set_variable(key, val):
    setattr(_threadlocals, key, val)

def get_variable(key, default=None):
    return getattr(_threadlocals, key, default)

def get_current_context():
    return get_variable('context', None)

def get_current_translator():
    return get_variable('translator', None)

def set_current_context(context):
    set_variable('context', context)

def set_current_translator(translator):
    set_variable('translator', translator)
