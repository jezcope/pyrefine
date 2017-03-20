class Operation:

    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

    def execute(self, data):
        return data


class MassEditOperation(Operation):

    def __init__(self, parameters):
        self.description = parameters['description']
        self.column = parameters['columnName']
        self.edits = parameters['edits']

    def execute(self, data):
        for edit in self.edits:
            for replace in edit['from']:
                data.loc[data[self.column] == replace, self.column] = edit['to']

        return data

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
