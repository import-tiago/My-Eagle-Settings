import json
from builtins import object

class Object(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False)

    def add(self, key, value):
        self.__dict__[key] = value