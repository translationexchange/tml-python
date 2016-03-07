from __future__ import absolute_import
# encoding: UTF-8
from ..exceptions import Error
from .__init__ import Set, system_tags, Tag, UnsupportedTag
import six

BEGIN_TOKEN = '['
END_TOKEN = ']'
CLOSE_TOKEN = '/'
TOKEN_SEPARATOR = ':'

class ShortTag(Tag):
    """ Short tag (like [b: text] """
    def __init__(self, tag):
        super(ShortTag, self).__init__(tag.name, tag.tag, tag.attributes)

    def append(self, el):
        if el == ' ' and len(self.text) == 0 and len(self.content) == 0:
            # ignore first space like [b: hello]
            return
        super(ShortTag, self).append(el)


class EmptyStack(Error):
    pass

def trace(*args):
    pass

def parse(text, tags_factory = None):
    """ Text parser """
    tags_factory = tags_factory or system_tags # use system factory
    pos = 0
    tag_name = None # [tag_name]
    close = False # inside [/close] token
    stack = []

    def end(element):
        # Tag closed:
        ret = stack.pop()
        ret.append(element)
        return ret

    element = Set()
    for let in text:
        try:
            if let == BEGIN_TOKEN:
                # Open some token [blah-blah]
                if not tag_name is None:
                    raise UnexpectedToken(text, pos)
                trace('begin token')
                tag_name = ''
            elif let == CLOSE_TOKEN:
                if tag_name is None:  # just a symbol
                    element.append(let)
                elif isinstance(element, ShortTag):
                    raise UnexpectedToken(text, pos, '[/')
                else:
                    close = True
            elif let == END_TOKEN:
                if close:
                    # Finish of tag: [b]bold[/b^]
                    if not isinstance(element, Tag) or tag_name != element.name:
                        raise UnexpectedToken(text, pos, BEGIN_TOKEN+CLOSE_TOKEN+tag_name+END_TOKEN)
                    # Pop and append:
                    element = end(element)
                    # Clean:
                    close = False
                    tag_name = None
                elif tag_name:
                    # Finish of tag definition [link^]site.com[/link]
                    new_element = tags_factory.build(tag_name)
                    if new_element.self_closed:
                        element.append(new_element)
                    else:
                        stack.append(element)
                        element = new_element
                    trace('build', tag_name)
                    tag_name = None
                elif element.__class__ is ShortTag:
                    # Finish of short tag: [i: text^]
                    element = end(element) # append current piece to short tag
                else:
                    if not tag_name:  # []
                        element.append(BEGIN_TOKEN)
                        element.append(END_TOKEN)
                        continue    
                    # raise UnexpectedToken(text, let)
    
            elif let == TOKEN_SEPARATOR:  # because it could be just a symbol
                # inside short token:
                if tag_name is None:
                    element.append(let)
                    continue
                stack.append(element)
                element = ShortTag(tags_factory.build(tag_name))
                trace('build short', tag_name)
                tag_name = None
            elif not tag_name is None:  # name of tag continue
                tag_name = tag_name + let
                trace('tag_name',tag_name)
            else:   # new symbol inside tag
                element.append(let)
        except UnsupportedTag as e:
            raise ParseError(text, pos, e)
        pos = pos + 1
    if len(stack):
        raise ParseError(text, pos-1, 'Element '+element.name+' is not closed')
    return element

class ParseError(Error):
    def __init__(self, text, pos, error):
        self.text = text
        self.pos = pos
        self.error = error

    def __str__(self, *args, **kwargs):
        return six.u('Decoration parsing fault on "%s" at %s with %s') % (self.text, self.pos, self.error)

class UnexpectedToken(ParseError):
    def __init__(self, text, pos, token = None):
        token = token if token else text[pos]
        super(UnexpectedToken, self).__init__(text, pos, 'unexpected %s' % token)


