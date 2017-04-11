"""Base class for all operations.

This module implements functionality common to all PyRefine operations. In
particular, it defines a base class, ``Operation`` and a metaclass
``OperationClass``, which between them ensure that all subclasses of
``Operation`` are automatically registered for use by the factory method
``Operation.create()``, which takes a dictionary of parameters as read from an
OpenRefine JSON script and returns an instance of an appropriate subclass.
"""
import re


class OperationClass(type):
    """Metaclass for operations.

    This is used as the metaclass for ``Operation`` which then automatically
    calls ``Operation._register()`` for each subclass, registers the operation
    for use by ``Operation.create()``.
    """

    def __init__(self, name, bases, namespace, **kwargs):
        """Register the operation at class initialisation."""
        super().__init__(name, bases, namespace)
        self._register(self.__operation_string(name), self)

    __camel_case_re = re.compile('([a-z])([A-Z])')

    def __operation_string(cls, classname):
        """Convert a class name FooBarOperation to a string "core/foo-bar".

        Strip off the last 9 characters of the classname ("Operation"),
        inserts a hyphen before each uppercase letter, then converts the
        whole thing to lowercase.
        """
        op_name = cls.__camel_case_re.sub(r'\1-\2', classname[:-9]) \
                                     .lower()
        return '{}/{}'.format(cls._or_module, op_name)


class Operation(metaclass=OperationClass):
    """Base class for all operations.

    All subclasses are automatically registered so they can be looked up on
    'op' field of the OpenRefine JSON format.
    """

    __operations = {}

    _or_module = "core"

    @classmethod
    def create(cls, parameters):
        """Construct an appropriate subclass of :class:`Operation`.

        This chooses the class based on the 'op' parameter.

        Args:
            parameters (:class:`dict`): A description of the operation to
                instantiate

        Returns:
            :class:`Operation`: An appropriate subclass of :class:`Operation`

        Raises:
            :exc:`RuntimeError`: If a class for the requested operation cannot
                be found.
        """
        op_name = parameters['op']
        if op_name not in cls.__operations:
            raise RuntimeError('Unknown operation "{}"'.format(op_name))

        return cls.__operations[op_name](parameters)

    @classmethod
    def _register(cls, op_name, op_class):
        """Register a class to handle the given operation."""
        cls.__operations[op_name] = op_class

    def __init__(self, *args, **kwargs):
        """Raise :exc:`NotImplementedError`."""
        raise NotImplementedError()
