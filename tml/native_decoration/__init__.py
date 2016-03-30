from ..config import CONFIG
from ..exceptions import Error
from .html import Html


installed_decorators = {
    'html': Html
}


class DecoratorNotInstalled(Error):
    pass


def get_decorator(application=None, options=None):
    options = {} if not options else options
    _decorator = CONFIG.decorator_class
    if options.get('decorator', None):
        _decorator = options['decorator']
    try:
        decorator_klass = installed_decorators.get(_decorator)
    except KeyError:
        raise DecoratorNotInstalled("install `%s` decorator.", _decorator)
    return decorator_klass(application)
