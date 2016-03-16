from .data import DataTokenizer


def execute_all(text, data, language, options=None):
    """ Execute all tokens
        Args:
            text (str): label to translate
            data (dict): context
            options (dict): execution options
        Returns:
            string: executed tokens
    """
    return DataTokenizer(text, data, options).substitute(language, options)
