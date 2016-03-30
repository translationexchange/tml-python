from __future__ import absolute_import
from __future__ import print_function
import functools
from ..session_vars import get_current_context
from .. import build_context
from ..context import LanguageContext


def context_configured(fn):

    @functools.wraps(fn)
    def _context_configured(tp_instance, *args, **kwargs):
        context = get_current_context()
        if context is None:
            build_context(context=LanguageContext)
            context = get_current_context()
        return fn(tp_instance, context, *args, **kwargs)

    return _context_configured
