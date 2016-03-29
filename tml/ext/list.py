import six
from .utils import context_configured


@context_configured
def translate(self, language_context, description='', options=None):
    options = {} if options is None else options
    if not self:
        return []
    return self
