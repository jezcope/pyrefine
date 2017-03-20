from .base import Operation
from .mass_edit import MassEditOperation


def create(parameters):
    op_name = parameters['op']
    if op_name not in OPERATIONS:
        raise RuntimeError('Unknown operation "{}"'.format(op_name))

    return OPERATIONS[op_name](parameters)


# TODO: Allow operations to register themselves here
# This list shouldn't be hard-coded! Need a decorator, maybe?
OPERATIONS = {
    'core/mass-edit': MassEditOperation,
}
