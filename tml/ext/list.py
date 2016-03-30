import six
from .str import translate as str_tr


# translates an array of options for a select tag
def tro(self, description='', options=None):
    if not self:
        return []
    options = {} if options is None else options
    options['nowrap'] = True
    for i, item in enumerate(self):
        if isinstance(item, six.string_types):
            item = [item, translate_str(item, description=description, data={}, options=options)]
        elif isinstance(item, (list, tuple)):
            item = [item[0], translate_str(item[1], description=description, data={}, options=options)]
        else:
            pass
        self[i] = item
    return self


def translate(self, description='', options=None):
    options = {} if options is None else options
    if not self:
        return []
    for i, item in enumerate(self):
        self[i] = translate_str(item, description=description, data={}, options=options)
    return self

def translate_str(string, **tr_kwargs):
    if not isinstance(string, six.string_types):
        return string
    if hasattr(string, 'tml_translate'):  # if patched
        return string.tml_translate(**tr_kwargs)
    else:   # otherwise use method
        return str_tr(string, **tr_kwargs)


def translate_and_join(self, separator=', ', description='', options=None):
    return separator.join(translate(self, description=description, options=options))

def translate_sentence(self, description='', options=None):
    options = {} if options is None else options
    options.setdefault('separator', ', ')
    options.setdefault('joiner', 'and')
    if not self:
        return ''
    elements = translate(self, description=description, options=options)
    if len(elements) == 1:
        return elements[0]
    str_builder = [options['separator'].join(elements[:-1])]
    str_builder.append(translate_str(options['joiner'], description=description or 'List elements joiner', data={}, options=options))
    str_builder.append(elements[-1])
    return u" ".join(str_builder)
