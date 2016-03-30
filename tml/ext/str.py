from __future__ import absolute_import
from __future__ import print_function
from .utils import context_configured


@context_configured
def translate(self, language_context, **tr_kwargs):
    return language_context.tr(self, **tr_kwargs)[1]


@context_configured
def trl(self, language_context, options=None, **tr_kwargs):
    options = {} if options is None else options
    options['nowrap'] = True
    return translate(self, options=options, **tr_kwargs)
