class Operation:

    def __init__(self, *args, **kwargs):
        raise NotImplementedError()


class MassEditOperation(Operation):

    def __init__(self, parameters):
        pass


def create(parameters):
    op_name = parameters['op']
    if op_name not in OPERATIONS:
        raise RuntimeError('Unknown operation "{}"'.format(op_name))

    return OPERATIONS[op_name](parameters)


# TODO: Allow operations to register themselves here
# This list shouldn't be hard-coded!
OPERATIONS = {
    'core/mass-edit': MassEditOperation,
}
