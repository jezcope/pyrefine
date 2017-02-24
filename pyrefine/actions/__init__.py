class Action:

    def __init__(self, *args, **kwargs):
        raise NotImplementedError()


class MassEditAction(Action):

    def __init__(self, parameters):
        pass


def create(parameters):
    if 'op' not in parameters:
        raise RuntimeError('No operation given')

    op = parameters['op']
    if op not in OPERATIONS:
        raise RuntimeError('Unknown operation "{}"'.format(op))
                                           
    constructor = OPERATIONS[parameters['op']]
    return constructor(parameters)

OPERATIONS = {
    'core/mass-edit': MassEditAction,
}
