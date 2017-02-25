# -*- coding: utf-8; -*-

import json


class Script(object):

    def __init__(self, s=None):
        if s is not None:
            self.parsed_script = json.loads(s)

    def __len__(self):
        return len(self.parsed_script)


def load_script(f):
    if isinstance(f, str):
        f = open(f)

    return parse(f.read())


def parse(s):
    return Script(s)
