# encoding: UTF-8
from . import use_source
from django.conf import settings
from django_tml import set_supports_inline_tranlation as _set_supports_inline_tranlation

save_supports_inline_tranlation = None

def set_supports_inline_tranlation(value):
    """ Turn off/on and remembed in cookies """
    global save_supports_inline_tranlation
    _set_supports_inline_tranlation(value)
    if settings.TML.get('inline_wrapper_cookie', None) is None:
        raise Exception('Cookie name for inline mode is not set')
    save_supports_inline_tranlation = value

class SetSourceToViewMiddleware(object):
    """ Create source to each view function """

    def process_request(self, request, *args, **kwargs):
        """ Handle wrapper cookie """
        cookie_name = settings.TML.get('inline_wrapper_cookie', None)
        if cookie_name is None:
            return None
        try:
            if request.get_signed_cookie(cookie_name):
                set_supports_inline_tranlation(True)
        except KeyError:
            # cookie is not set
            pass
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Use source based on view function """
        use_source('%s.%s' % (view_func.__module__, view_func.__name__))
        return None

    def process_response(self, request, response):
        """ Reset source and flush missed keys """
        use_source(None)
        _set_supports_inline_tranlation(False)
        return self.set_cookie_for_inline_translation(response)

    def set_cookie_for_inline_translation(self, response):
        """ Set cookie """
        global save_supports_inline_tranlation
        if save_supports_inline_tranlation is None:
            return response
        cookie_name = settings.TML.get('inline_wrapper_cookie', None)
        if cookie_name is None:
            return response
        response.set_signed_cookie(cookie_name, save_supports_inline_tranlation)
        return response

