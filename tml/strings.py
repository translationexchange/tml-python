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
    return unicode(text.decode('utf-8'))


