# encoding: UTF-8
from ..exceptions import Error

def render_attributes(attributes):
    if attributes is None or len(attributes) == 0:
        return ''
    return ' %s' % ' '.join([render_attribute(key, attributes[key]) for key in attributes])

def render_attribute(key, value):
    return '%s="%s"' % (key, value.replace('"', '&quot;'))

class Text(object):
    """ Plain text node """
    def __init__(self, text = ''):
        self.text = text

    def append(self, let):
        self.text = self.text + let
        return self

    def render(self, data = {}):
        """ Just return text """
        return self.text

    def __len__(self):
        return len(self.text)


class Set(object):
    """ Nodes list """
    def __init__(self):
        self.content = []
        self.text = Text()

    def append(self, el):
        if type(el) is str or type(el) is unicode:
            self.text.append(el)
        else:
            self.flush_text()
            self.content.append(el)
        return self

    def flush_text(self):
        if len(self.text):
            self.content.append(self.text)
            self.text = Text()

    def render(self, data = None):
        self.flush_text()
        return ''.join(el.render(data) for el in self.content)

class AttributeIsNotSet(Error):
    def __init__(self, name, key):
        self.name = name
        self.key = key

    def __str__(self):
        return 'Attribute %s is not passed to '


class Tag(Set):
    """ Tag element """
    def __init__(self, name = None, tag = None, attributes = []):
        self.name = name
        self.tag = tag
        self.attributes = attributes
        super(Tag, self).__init__()

    def render(self, data = None):
        attributes = {}
        for key in self.attributes:
            try:
                attributes[key] = data[self.name][key]
            except Exception:
                raise AttributeIsNotSet(self.name, key)
        return '<%s%s>%s</%s>' % (self.tag, render_attributes(attributes), super(Tag, self).render(data), self.tag)


class TagFactory(object):
    """ Tags factory """
    def __init__(self, allowed_tags = {}):
        self.allowed_tags = allowed_tags

    def build(self, name):
        try:
            return Tag(name, *self.allowed_tags[name])
        except KeyError:
            raise UnsupportedTag(name, self)

    def allow(self, name, tag, attributes = {}):
        self.allowed_tags[name] = (tag, attributes)
        return self

    @property
    def supported_tags(self):
        return self.allowed_tags.keys()


class UnsupportedTag(Error):
    """ Tag is not supported by factory """
    def __init__(self, name, factory):
        self.name = name
        self.factory = factory

    def __str__(self, *args, **kwargs):
        return 'Tag %s is not supported' % self.name


system_tags = TagFactory()
system_tags.allow('link', 'a', ['href'])
system_tags.allow('a', 'a', ['href'])
system_tags.allow('b', 'strong')
system_tags.allow('i', 'i')
system_tags.allow('-', 'strike')

