# flake8: noqa

import pytest

import pandas as pd
import numpy as np
import pandas.util.testing as pdt

from collections.abc import Callable

import pyrefine


def assert_op_changes_data(params, *, base_data, expected_data):
    op = pyrefine.ops.create(params)
    actual_data = op(base_data)

    pdt.assert_frame_equal(expected_data, actual_data)

def assert_op_raises(params, data, exception):
    op = pyrefine.ops.create(params)
    with pytest.raises(exception):
        op(data)


class TestOperation:

    def test_create_no_operation(self):
        with pytest.raises(KeyError):
            pyrefine.ops.create({})

    def test_create_unknown_operation(self):
        with pytest.raises(RuntimeError):
            pyrefine.ops.create({'op': 'does not exist'})


class CommonOperationTests:

    def test_create_with_valid_params(self, default_params):
        op = pyrefine.ops.create(default_params)

        assert op is not None
        assert isinstance(op, Callable)

    def test_input_immutable(self, default_params, base_data):
        op = pyrefine.ops.create(default_params)
        orig_data = base_data.copy()

        op(base_data)
        pdt.assert_frame_equal(orig_data, base_data)


class TestMassEditOperation(CommonOperationTests):

    op_class = pyrefine.ops.MassEditOperation

    @pytest.fixture
    def default_params(self):
        return {'columnName': 'needs_fixing',
                'description': 'Test mass edit',
                'edits': [{'from': ['wrong'],
                           'fromBlank': False,
                           'fromError': False,
                           'to': 'right'}],
                'engineConfig': {'facets': [], 'mode': 'row-based'},
                'expression': 'value',
                'op': 'core/mass-edit'}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame({
            'other': 'one two three four five'.split(),
            'needs_fixing': ['wrong', 'right', 'wrong', 'questionable',
                             None],
            'age': np.random.randint(18, 70, 5)})

    def test_single_edit(self, base_data, default_params):
        assert_op_changes_data(
            default_params,
            base_data=base_data,
            expected_data=base_data.assign(
                needs_fixing=['right', 'right', 'right',
                              'questionable', None]))

    def test_single_edit_numeric(self, base_data, default_params):
        assert_op_changes_data(
            dict(default_params,
                 edits=[{'from': [200, 2000],
                         'fromBlank': False,
                         'fromError': False,
                         'to': 20}]),
            base_data=base_data.assign(
                needs_fixing=[123, 78, 200, 20, 2000]),
            expected_data=base_data.assign(
                needs_fixing=[123, 78, 20, 20, 20]))

    def test_multiple_edits(self, base_data, default_params):
        assert_op_changes_data(
            dict(default_params,
                 edits=[{'from': ['wrong'], 'to': 'right',
                         'fromBlank': False, 'fromError': False},
                        {'from': ['questionable'], 'to': '?',
                         'fromBlank': False, 'fromError': False}]),
            base_data=base_data,
            expected_data=base_data.assign(
                needs_fixing=['right', 'right', 'right', '?', None]))

    def test_fromblank_edit(self, base_data, default_params):
        assert_op_changes_data(
            dict(default_params,
                 edits=[{'from': [], 'to': 'not blank',
                         'fromBlank': True,
                         'fromError': False}]),
            base_data=base_data,
            expected_data=base_data.assign(
                needs_fixing=['wrong', 'right', 'wrong',
                              'questionable', 'not blank']))

    def test_multivalued_cell(self, base_data, default_params):
        assert_op_changes_data(
            default_params,
            base_data=base_data.assign(
                needs_fixing=['wrong', 'right',
                              ['wrong', 'foo bar', 'baz', 'wrong'],
                              'questionable', ['right', 'wrong']]),
            expected_data=base_data.assign(
                needs_fixing=['right', 'right',
                              ['right', 'foo bar', 'baz', 'right'],
                              'questionable', ['right', 'right']]))


class TestBlankDownOperation(CommonOperationTests):

    @pytest.fixture
    def default_params(self):
        return {"op": "core/blank-down",
                "description": "Blank down cells in column tidy_up",
                "engineConfig": {
                    "mode": "row-based",
                    "facets": []
                },
                "columnName": "tidy_up"}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame({'id': np.arange(10),
                             'tidy_up': ['one', 'two', 'two', 'three', 'four',
                                         'four', 'four', 'four', 'five', 'five']})

    def test_blank_down(self, default_params, base_data):
        assert_op_changes_data(
            default_params,
            base_data=base_data,
            expected_data=base_data.assign(
                tidy_up=['one', 'two', None, 'three', 'four',
                         None, None, None, 'five', None]))


class TestFillDownOperation(CommonOperationTests):

    @pytest.fixture
    def default_params(self):
        return {"op": "core/fill-down",
                "description": "Fill down cells in column tidy_up",
                "engineConfig": {
                    "mode": "row-based",
                    "facets": []
                },
                "columnName": "tidy_up"}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame({'id': np.arange(10),
                             'tidy_up': ['one', 'two', None, 'three', 'four',
                                         None, None, None, 'five', None]})

    def test_fill_down(self, default_params, base_data):
        assert_op_changes_data(
            default_params,
            base_data=base_data,
            expected_data=base_data.assign(
                tidy_up=['one', 'two', 'two', 'three', 'four',
                         'four', 'four', 'four', 'five', 'five']))


class TestMultivaluedCellSplitOperation(CommonOperationTests):

    @pytest.fixture
    def default_params(self):
        return {"op": "core/multivalued-cell-split",
                "description": "Split multi-valued cells in column split_me",
                "columnName": "split_me",
                "keyColumnName": "Title",
                "separator": "|",
                "mode": "plain"}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame({'id': np.arange(3),
                             'split_me': ['Split|these|up',
                                          'No splitting here',
                                          'Item 1|item 2|item_3']})

    def test_split_column(self, default_params, base_data):
        assert_op_changes_data(
            default_params,
            base_data=base_data,
            expected_data=base_data.assign(
                split_me=[['Split', 'these', 'up'],
                          ['No splitting here'],
                          ['Item 1', 'item 2', 'item_3']]))

    def test_split_numeric_column(self, default_params, base_data):
        assert_op_raises(dict(default_params, columnName='id'),
                         base_data, TypeError)

    def test_with_spaces(self, default_params, base_data):
        assert_op_changes_data(
            default_params,
            base_data=base_data.assign(
                split_me=['This|  has|  some |spaces ',
                          'No splitting here ',
                          'Item 1|item 2|item_3']),
            expected_data=base_data.assign(
                split_me=[['This', 'has', 'some', 'spaces'],
                          ['No splitting here '],
                          ['Item 1', 'item 2', 'item_3']]))


class TestMultivaluedCellJoinOperation(CommonOperationTests):

    @pytest.fixture
    def default_params(self):
        return {"op": "core/multivalued-cell-join",
                "description": "Join multi-valued cells in column split_me",
                "columnName": "join_me",
                "keyColumnName": "Title",
                "separator": "|",
                "mode": "plain"}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame({'id': np.arange(3),
                             'join_me': [['Join', 'these', 'up'],
                                         ['No splitting here'],
                                         ['Item 1', 'item 2', 'item_3']]})

    def test_split_column(self, default_params, base_data):
        assert_op_changes_data(
            default_params,
            base_data=base_data,
            expected_data=base_data.assign(
                join_me=['Join|these|up',
                         'No splitting here',
                         'Item 1|item 2|item_3']))

    def test_split_numeric_column(self, default_params, base_data):
        assert_op_raises(dict(default_params, columnName='id'),
                         base_data, TypeError)


class TestTransposeRowsIntoColumnsOperation(CommonOperationTests):

    @pytest.fixture
    def default_params(self):
        return {"op": "core/transpose-rows-into-columns",
                "description": "Transpose every 2 cells in column transpose into separate columns",
                "columnName": "transpose",
                "rowCount": 2}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame({'id': np.arange(10),
                             'transpose': ['one', 'two', 'three', 'four', 'five',
                                           'six', 'seven', 'eight', 'nine', 'ten']})

    def test_transpose_two_rows(self, default_params, base_data):
        expected_data = base_data.copy()
        del expected_data['transpose']
        expected_data['transpose 1'] = ['one', None, 'three', None, 'five',
                                        None, 'seven', None, 'nine', None]
        expected_data['transpose 2'] = ['two', None, 'four', None, 'six',
                                        None, 'eight', None, 'ten', None]

        assert_op_changes_data(
            default_params,
            base_data=base_data,
            expected_data=expected_data)

    def test_transpose_five_rows(self, default_params, base_data):
        expected_data = base_data.copy()
        del expected_data['transpose']
        expected_data['transpose 1'] = ['one', None, None, None, None,
                                        'six', None, None, None, None]
        expected_data['transpose 2'] = ['two', None, None, None, None,
                                        'seven', None, None, None, None]
        expected_data['transpose 3'] = ['three', None, None, None, None,
                                        'eight', None, None, None, None]
        expected_data['transpose 4'] = ['four', None, None, None, None,
                                        'nine', None, None, None, None]
        expected_data['transpose 5'] = ['five', None, None, None, None,
                                        'ten', None, None, None, None]

        assert_op_changes_data(
            dict(default_params, rowCount=5),
            base_data=base_data,
            expected_data=expected_data)


    def test_transpose_three_rows(self, default_params, base_data):
        expected_data = base_data.copy()
        del expected_data['transpose']
        expected_data['transpose 1'] = ['one', None, None, 'four', None,
                                        None, 'seven', None, None, 'ten']
        expected_data['transpose 2'] = ['two', None, None, 'five', None,
                                        None, 'eight', None, None, None]
        expected_data['transpose 3'] = ['three', None, None, 'six', None,
                                        None, 'nine', None, None, None]

        assert_op_changes_data(
            dict(default_params, rowCount=3),
            base_data=base_data,
            expected_data=expected_data)


    def test_transpose_two_rows_numeric(self, default_params, base_data):
        base_data['transpose'] = np.arange(10)
        expected_data = base_data.copy()
        del expected_data['transpose']
        expected_data['transpose 1'] = [0, np.NaN, 2, np.NaN, 4,
                                        np.NaN, 6, np.NaN, 8, np.NaN]
        expected_data['transpose 2'] = [1, np.NaN, 3, np.NaN, 5,
                                        np.NaN, 7, np.NaN, 9, np.NaN]

        assert_op_changes_data(
            default_params,
            base_data=base_data,
            expected_data=expected_data)


class TestColumnRemovalOperation(CommonOperationTests):

    @pytest.fixture
    def default_params(self):
        return {"op": "core/column-removal",
                "description": "Remove column remove_me",
                "columnName": "remove_me"}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame({'keep_me': np.arange(20),
                             'remove_me': np.arange(20)})

    def test_remove_column(self, default_params, base_data):
        op = pyrefine.ops.create(default_params)
        actual_data = op(base_data)

        assert 'remove_me' not in actual_data.columns
        assert 'keep_me' in actual_data.columns


class TestColumnRenameOperation(CommonOperationTests):

    @pytest.fixture
    def default_params(self):
        return {"op": "core/column-rename",
                "description": "Rename column oldname to blah",
                "oldColumnName": "oldname",
                "newColumnName": "blah"}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame({'keep_me': np.arange(20),
                             'oldname': np.arange(20)})

    def test_rename_column(self, default_params, base_data):
        op = pyrefine.ops.create(default_params)
        actual_data = op(base_data)

        assert 'oldname' not in actual_data.columns
        assert 'blah' in actual_data.columns
        pdt.assert_series_equal(actual_data.blah,
                                base_data.oldname.rename("blah"))


class TestColumnMoveOperation(CommonOperationTests):

    @pytest.fixture
    def default_params(self):
        return {"op": "core/column-move",
                "description": "Move column third to position 0",
                "columnName": "third",
                "index": 0}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame(np.eye(4, dtype=int),
                            columns='first second third fourth'.split())

    def test_move_column_to_start(self, default_params, base_data):
        assert_op_changes_data(
            default_params,
            base_data=base_data,
            expected_data=pd.DataFrame([[0, 1, 0, 0],
                                        [0, 0, 1, 0],
                                        [1, 0, 0, 0],
                                        [0, 0, 0, 1]],
                                       columns='third first second fourth'.split()))
    def test_move_column_to_end(self, default_params, base_data):
        assert_op_changes_data(
            dict(default_params, columnName='third', index=3),
            base_data=base_data,
            expected_data=pd.DataFrame([[1, 0, 0, 0],
                                        [0, 1, 0, 0],
                                        [0, 0, 0, 1],
                                        [0, 0, 1, 0]],
                                       columns='first second fourth third'.split()))

    def test_move_column_to_right(self, default_params, base_data):
        assert_op_changes_data(
            dict(default_params, columnName='second', index=2),
            base_data=base_data,
            expected_data=pd.DataFrame([[1, 0, 0, 0],
                                        [0, 0, 1, 0],
                                        [0, 1, 0, 0],
                                        [0, 0, 0, 1]],
                                       columns='first third second fourth'.split()))

    def test_move_column_before_start(self, default_params, base_data):
        assert_op_raises(dict(default_params, columnName='third', index=-2),
                         base_data, IndexError)

    def test_move_column_after_end(self, default_params, base_data):
        assert_op_raises(dict(default_params, columnName='third', index=4),
                         base_data, IndexError)

    def test_move_non_existent_column(self, default_params, base_data):
        assert_op_raises(dict(default_params, columnName='seventh', index=2),
                         base_data, KeyError)


class TestColumnMoveOperation(CommonOperationTests):

    @pytest.fixture
    def default_params(self):
        return {"op": "core/column-reorder",
                "description": "Reorder columns",
                "columnNames": 'third first second fourth'.split()}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame(np.eye(4, dtype=int),
                            columns='first second third fourth'.split())

    def test_simple_reorder_columns(self, default_params, base_data):
        assert_op_changes_data(
            default_params,
            base_data=base_data,
            expected_data=pd.DataFrame([[0, 1, 0, 0, ],
                                        [0, 0, 1, 0, ],
                                        [1, 0, 0, 0, ],
                                        [0, 0, 0, 1, ]],
                                       columns='third first second fourth'.split()))

    def test_reverse_columns(self, default_params, base_data):
        assert_op_changes_data(
            dict(default_params,
                 columnNames='fourth third second first'.split()),
            base_data=base_data,
            expected_data=pd.DataFrame([[0, 0, 0, 1, ],
                                        [0, 0, 1, 0, ],
                                        [0, 1, 0, 0, ],
                                        [1, 0, 0, 0, ]],
                                       columns='fourth third second first'.split()))

    def test_remove_columns(self, default_params, base_data):
        assert_op_changes_data(
            dict(default_params,
                 columnNames='fourth first'.split()),
            base_data=base_data,
            expected_data=pd.DataFrame([[0, 1, ],
                                        [0, 0, ],
                                        [0, 0, ],
                                        [1, 0, ]],
                                       columns='fourth first'.split()))


class TestColumnAdditionOperation(CommonOperationTests):

    @pytest.fixture
    def default_params(self):
        return {"op": "core/column-addition",
                "description": "Create new column based on expression",
                "engineConfig": {
                    "mode": "row-based",
                    "facets": []
                },
                "newColumnName": "fifth",
                "columnInsertIndex": 4,
                "baseColumnName": "second",
                "expression": "jython:return value + 10",
                "onError": "set-to-blank"}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame(np.eye(4, dtype=int),
                            columns='first second third fourth'.split())

    def test_executes_expression(self, default_params, base_data):
        assert_op_changes_data(
            default_params,
            base_data=base_data,
            expected_data=base_data.assign(
                fifth=[10, 11, 10, 10]))

    def test_inserts_at_correct_index(self, default_params, base_data):
        op = pyrefine.ops.create(
            dict(default_params, columnInsertIndex=1))

        actual_data = op(base_data)

        pdt.assert_index_equal(
            actual_data.columns,
            pd.Index('first fifth second third fourth'.split()))


    def test_blank_on_error(self, default_params, base_data):
        assert_op_changes_data(
            dict(default_params,
                 onError='set-to-blank',
                 expression='jython:raise RuntimeError()'),
            base_data=base_data,
            expected_data=base_data.assign(
                fifth=[None, None, None, None]))

    def test_keep_original_on_error(self, default_params, base_data):
        assert_op_changes_data(
            dict(default_params,
                 onError='keep-original',
                 expression='jython:raise RuntimeError()'),
            base_data=base_data,
            expected_data=base_data.assign(
                fifth=base_data.second))

    def test_store_error(self, default_params, base_data):
        op = pyrefine.ops.create(
            dict(default_params,
                 onError='store-error',
                 expression='jython:raise RuntimeError()'))

        actual_data = op(base_data)

        for i, value in enumerate(actual_data.fifth):
            assert isinstance(value, RuntimeError), f'{i}: {value}'
