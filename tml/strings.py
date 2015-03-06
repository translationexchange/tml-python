# encoding: UTF-8
def to_string(text):
    """ Safe string conversion 
        Args:
            text (string|unicode): input string
        Returns:
            str
    """
    if text is unicode:
        return text.encode('utf-8')
    return text

