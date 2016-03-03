import json

class JSONCodec(object):

    def __init__(self, file, protocol=None):
        self.file = file

    def dump(self, value):
        json.dump(value, self.file)

    def load(self):
        return json.load(self.file)
