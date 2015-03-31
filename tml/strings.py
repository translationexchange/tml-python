# encoding: UTF-8
def to_string(text):
    """ Safe string conversion 
        Args:
            text (string|unicode): input string
        Returns:
            str
    """
    if type(text) is unicode:
        return text
    if hasattr(text, '__html__'):
        return unicode(text.__html__())
    if hasattr(text, '__unicode__'):
        return text.__unicode__()
    return unicode(str(text).decode('utf-8'))


SUGGEST_STRING_KEYS = ['title','name','html','text']

def suggest_string(data):
    if type(data) is dict:
        for key in SUGGEST_STRING_KEYS:
            if key in data:
                return data[key]
        for key in data:
            # Return first key:
            return dict[key]
    return data

