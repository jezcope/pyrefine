class Operation:

    __operations = {}

    @classmethod
    def create(cls, parameters):
        """Construct an appropriate subclass of ``Operation``.

        This chooses the class based on the 'op' parameter.
        """
        op_name = parameters['op']
        if op_name not in cls.__operations:
            raise RuntimeError('Unknown operation "{}"'.format(op_name))

        return cls.__operations[op_name](parameters)

    @classmethod
    def register(cls, op_name, op_class):
        """Register a class to handle the given operation."""
        cls.__operations[op_name] = op_class

    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

    def execute(self, data):
        return data
