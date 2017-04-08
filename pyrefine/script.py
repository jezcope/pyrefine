# -*- coding: utf-8; -*-

import json

from .ops import Operation


class Script(object):

    def __init__(self, s=None):
        if s is not None:
            self.parsed_script = json.loads(s)
            self.operations = [Operation.create(params)
                               for params in self.parsed_script]

    def __len__(self):
        return len(self.operations)

    def execute(self, data):
        for op in self.operations:
            data = op.execute(data)

        return data


def load_script(f):
    if isinstance(f, str):
        f = open(f)

    return parse(f.read())


def parse(s):
    return Script(s)
