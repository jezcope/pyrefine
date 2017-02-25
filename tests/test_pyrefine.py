#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pyrefine
----------------------------------

Tests for `pyrefine` module.
"""

import pytest

# from contextlib import contextmanager
# from click.testing import CliRunner

import os.path

import pyrefine
# from pyrefine import cli

# class TestCLI:

#     def test_command_line_interface(self):
#         runner = CliRunner()
#         result = runner.invoke(cli.main)
#         assert result.exit_code == 0
#         assert 'pyrefine.cli.main' in result.output
#         help_result = runner.invoke(cli.main, ['--help'])
#         assert help_result.exit_code == 0
#         assert '--help  Show this message and exit.' in help_result.output


class TestScript:

    def test_load_file_object(self):
        with open(os.path.dirname(__file__)
                  + '/fixtures/example_script.json') as f:
            script = pyrefine.load_script(f)

        assert script is not None
        assert isinstance(script, pyrefine.Script)

    def test_load_file_name(self):
        script = pyrefine.load_script(os.path.dirname(__file__)
                                      + '/fixtures/example_script.json')

        assert script is not None
        assert isinstance(script, pyrefine.Script)

    def test_load_string(self):
        with open(os.path.dirname(__file__)
                  + '/fixtures/example_script.json') as f:
            script_string = f.read()

        script = pyrefine.parse(script_string)

        assert script is not None
        assert isinstance(script, pyrefine.Script)
        assert len(script) == 1

    def test_empty_script(self):
        script = pyrefine.parse("[]")

        assert script is not None
        assert isinstance(script, pyrefine.Script)
        assert len(script) == 0


class TestOperations:

    def test_create_no_operation(self):
        with pytest.raises(KeyError):
            pyrefine.ops.create({})

    def test_create_unknown_action(self):
        with pytest.raises(RuntimeError):
            pyrefine.ops.create({'op': 'does not exist'})


class TestMassEditOperation:

    def test_create_valid_params(self):
        parameters = {'columnName': 'country',
                      'description': 'Mass edit cells in column country',
                      'edits': [{'from': ['Cura%C3%A7ao'],
                                 'fromBlank': False,
                                 'fromError': False,
                                 'to': 'Curacao'}],
                      'engineConfig': {'facets': [], 'mode': 'row-based'},
                      'expression': 'value',
                      'op': 'core/mass-edit'}
        action = pyrefine.ops.create(parameters)

        assert action is not None
        assert isinstance(action, pyrefine.ops.MassEditOperation)
