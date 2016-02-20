from __future__ import absolute_import
# encoding: UTF-8
from ..exceptions import Error
import six

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
        if isinstance(el, six.string_types) or type(el) is six.text_type:
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
        super(AttributeIsNotSet, self).__init__()
        self.name = name
        self.key = key

    def __str__(self):
        return 'Attribute %s for %s is not passed' % (self.key, self.name)


class Tag(Set):
    """ Tag element """
    def __init__(self, name = None, tag = None, attributes = [], self_closed = False):
        self.name = name
        self.tag = tag
        self.attributes = attributes
        self.self_closed = self_closed
        super(Tag, self).__init__()

    def render(self, data = None):
        attributes = {}
        first = True
        for key in self.attributes:
            try:
                attributes[key] = self.fetch_attribute(key, data)
            except Exception as e:
                raise AttributeIsNotSet(self.name, key)
            first = False
        if self.self_closed:
            return '<%s/>%s' % (self.tag, super(Tag, self).render(data))
        return '<%s%s>%s</%s>' % (self.tag, render_attributes(attributes), super(Tag, self).render(data), self.tag)

    def fetch_attribute(self, key, attributes):
        """ Fetch attibute by key
            Args:
                key (string): attribute name
            Retursn:
                string: attribute links
        """
        long_key = '%s_%s' % (self.name, key)
        try:
            # Use long key like "link_href"
            return attributes[long_key]
        except Exception:
            pass
        try:
            # Use attribute as dict
            return attributes[self.name][key]
        except Exception:
            pass
        if isinstance(attributes[self.name], six.string_types) and len(self.attributes) == 1:
            # just link
            return attributes[self.name]


class TagFactory(object):
    """ Tags factory """
    def __init__(self, allowed_tags = {}):
        self.allowed_tags = allowed_tags

    def build(self, name):
        try:
            return Tag(name, *self.allowed_tags[name])
        except KeyError:
            raise UnsupportedTag(name, self)

    def allow(self, name, tag = None, attributes = [], self_closed = False):
        if tag is None:
            tag = name
        self.allowed_tags[name] = (tag, attributes, self_closed)
        return self

    @property
    def supported_tags(self):
        return list(self.allowed_tags.keys())


class UnsupportedTag(Error):
    """ Tag is not supported by factory """
    def __init__(self, name, factory):
        self.name = name
        self.factory = factory

    def __str__(self, *args, **kwargs):
        return 'Tag %s is not supported' % self.name


system_tags = TagFactory()

system_tags.allow('strong', 'strong')
system_tags.allow('bold', 'strong')
system_tags.allow('b', 'strong')
system_tags.allow('em', 'em')
system_tags.allow('italic', 'i')
system_tags.allow('i', 'i')
system_tags.allow('br', 'br', [], self_closed = True)
system_tags.allow('link', 'a', ['href'])
system_tags.allow('a', 'a', ['href'])
system_tags.allow('-', 'strike')
system_tags.allow('strike', 'strike')
system_tags.allow('h1')
system_tags.allow('h2')
system_tags.allow('h3')
system_tags.allow('div', 'div', ['id','class','style'])
system_tags.allow('span', 'span', ['id','class','style'])


