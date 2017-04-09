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
                                        .apply(self._transform,
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
    def _transform(cls, val, from_val, to_val):
        if val == from_val:
            return to_val
        elif type(val) is list:
            return [cls._transform(x, from_val, to_val) for x in val]
        else:
            return val


class MultivaluedCellSplitOperation(Operation):

    def __init__(self, parameters):
        self.description = parameters['description']
        self.column = parameters['columnName']
        self.separator = parameters['separator']

    def transform(self, value):
        if self.separator in value:
            return list(map(str.strip, value.split(self.separator)))
        else:
            return [value]

    def execute(self, data):
        try:
            return data.assign(**{self.column:
                                  data[self.column].apply(self.transform)})
        except AttributeError:
            raise TypeError('Non-string data found in column "{}"'
                            .format(self.column))


class MultivaluedCellJoinOperation(Operation):

    def __init__(self, parameters):
        self.description = parameters['description']
        self.column = parameters['columnName']
        self.separator = parameters['separator']

    def transform(self, value):
        return self.separator.join(value)

    def execute(self, data):
        try:
            return data.assign(**{self.column:
                                  data[self.column].apply(self.transform)})
        except AttributeError:
            raise TypeError('Non-string data found in column "{}"'
                            .format(self.column))
