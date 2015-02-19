import re
IS_TOKEN = re.compile('(\{.*?\})')

def tokenize(str):
    return IS_TOKEN.split(str)

class StringToken(object):
    def __init__(self, str):
        self.str = str

    def execute(self, data):
        return self.str

class Token(object):
    def __init__(self, key):
        self.key = key

    def execute(self, data):
        return u'%s' % data[key]

    def fetch(self, data):
        return data[key]

class RulesToken(Token):
    def __init__(self, key, rules):
        self.key = key
        self.rules = self.rules

    def execute(self, data):
        ret = self.fetch(data)
        for rule in RULES:
            try:
                return rule.apply(ret, self.rules)
            except UnsupportedType:
                pass
        return None

class PipedToken(Token):
    def __init__(self, key, rules):
        self.rules = RulesToken(key, rules)
        self.key = key

    def execute(self, data):
        return '%s%s' % (super(PipedToken, self).execute(data), self.rules.execute(data))
                