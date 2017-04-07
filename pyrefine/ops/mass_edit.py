from .base import Operation


class MassEditOperation(Operation):

    def __init__(self, parameters):
        self.description = parameters['description']
        self.column = parameters['columnName']
        self.edits = parameters['edits']

    def execute(self, data):
        for edit in self.edits:
            for replace in edit['from']:
                # TODO: loop/condition order could probably be better
                if data[self.column].dtype == object:
                    data[self.column] = data[self.column] \
                                        .apply(self.__transform,
                                               from_val=replace,
                                               to_val=edit['to'])
                else:
                    data.loc[data[self.column] == replace, self.column] \
                        = edit['to']

            if edit['fromBlank']:
                data.loc[data[self.column].isnull(), self.column] \
                    = edit['to']

        return data

    @classmethod
    def __transform(cls, val, from_val, to_val):
        print(val, from_val, to_val)
        if val == from_val:
            return to_val
        elif type(val) is list:
            return [cls.__transform(x, from_val, to_val) for x in val]
        else:
            return val
