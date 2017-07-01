"""A script is a series of operations."""

import json
import os

from .ops import create


class Script(object):
    """A script is a series of operations."""

    def __init__(self, s=None):
        """Parse a script from a JSON string."""
        if s is not None:
            self.parsed_script = json.loads(s)
            self.operations = [create(params)
                               for params in self.parsed_script]

    def __len__(self):
        """Return the number of operations."""
        return len(self.operations)

    def execute(self, data):
        """Execute all operations on the provided dataset.

        Args:
            data (:class:`pandas.DataFrame`): The data to transform. Not
                guaranteed immutable.

        Returns:
            :class:`pandas.DataFrame`: The transformed data.

        """
        for op in self.operations:
            data = op(data)

        return data


def load_script(f):
    """Load and parse the script given.

    Args:
        f (:class:`file` or :class:`str`): Open file object or filename.

    Returns:
        :class:`Script`: The parsed script object.

    """
    if isinstance(f, (str, os.PathLike)):
        f = open(f)

    with f:
        return parse(f.read())


parse = Script
