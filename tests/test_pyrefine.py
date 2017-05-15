#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pyrefine
----------------------------------

Tests for `pyrefine` module.
"""

# flake8: noqa

import pytest

# from contextlib import contextmanager
from click.testing import CliRunner

import os.path
from tempfile import mktemp
import pandas as pd
import pandas.util.testing as pdt

import pyrefine
from pyrefine import cli


@pytest.fixture
def doaj_data_filename():
    return os.path.join(os.path.dirname(__file__),
                        'fixtures/doaj-article-sample.csv')


@pytest.fixture
def doaj_data(doaj_data_filename):
    return pd.read_csv(doaj_data_filename)


@pytest.fixture
def doaj_data_clean_filename():
    return os.path.join(os.path.dirname(__file__),
                        'fixtures/doaj-article-sample-cleaned.csv')


@pytest.fixture
def doaj_data_clean(doaj_data_clean_filename):
    return pd.read_csv(doaj_data_clean_filename)


@pytest.fixture
def doaj_script_filename():
    return os.path.join(os.path.dirname(__file__),
                        'fixtures/doaj-article-clean.json')


@pytest.fixture
def doaj_script(doaj_script_filename):
    return open(doaj_script_filename).read()


class TestCLI:

    def test_command_line_interface(self):
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'pyrefine' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output

    def test_cli_execute_stdout(self, doaj_script_filename,
                                doaj_data_filename,
                                doaj_data_clean_filename):
        runner = CliRunner()
        result = runner.invoke(cli.execute,
                               [doaj_script_filename, doaj_data_filename])

        expected_data = open(doaj_data_clean_filename).read()

        assert result.exit_code == 0
        assert result.output == expected_data

    def test_cli_execute_outfile(self, doaj_script_filename,
                                 doaj_data_filename,
                                 doaj_data_clean_filename):
        runner = CliRunner()
        out_file = mktemp()
        result = runner.invoke(cli.execute,
                               [doaj_script_filename, doaj_data_filename,
                                '-o', out_file])
        expected_data = open(doaj_data_clean_filename).read()

        assert result.exit_code == 0
        actual_data = open(out_file).read()

        assert actual_data == expected_data


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

    def test_whole_script(self, doaj_data, doaj_data_clean, doaj_script):
        script = pyrefine.parse(doaj_script)

        result = script.execute(doaj_data)

        pdt.assert_frame_equal(result, doaj_data_clean)
