"""Registry of available operations.

This module provides two key functions: :func:`create` constructs an instance
of an operation based on a provided dictionary of parameters;
:func:`operation` decorates a class and registers it to handle a named
operation.
"""

_operations = {}


def create(parameters):
    """Construct an appropriate subclass of :class:`Operation`.

    This chooses the class based on the 'op' parameter.

    Args:
        parameters (:class:`dict`): A description of the operation to
            instantiate

    Returns:
        ``object``: A configured instance of an appropriate operation class.

    Raises:
        :exc:`RuntimeError`: If a class for the requested operation cannot
            be found.

    """
    op_name = parameters['op']
    if op_name not in _operations:
        raise RuntimeError('Unknown operation "{}"'.format(op_name))

    return _operations[op_name](parameters)


def operation(name, mod='core'):
    """Register a class to handle the named operation.

    The class will be registered to handle the operation "{mod}/{name}" when
    it is encountered in a JSON script. ``mod`` will be "core" for all of the
    built-in OpenRefine operations, so that is the default, but this can be
    altered if implementing operations added by an OpenRefine plugin.

    Args:
        name (:class:`str`): Name of the operation to register. This
            is usually a lowercase string separated by hyphens ("-").
        mod (:class:`str`): Name of the OpenRefine module containing
            the given operation
    """
    def register_with_name(cls):
        _operations[mod + '/' + name] = cls
        return cls

    return register_with_name
