# Tests based on real-world examples of usage

import pytest
import pandas as pd
import pandas.util.testing as pdt

from .utils import FIXTURES_PATH

import pyrefine


@pytest.mark.xfail
def test_workshop_script():
    example = 'workshops'
    input_data = pd.read_csv(FIXTURES_PATH / f'{example}-raw.csv')
    expected_data = pd.read_csv(FIXTURES_PATH / f'{example}-clean.csv')
    script = pyrefine.load_script(FIXTURES_PATH / f'{example}-script.json')

    actual_data = script.execute(input_data)

    pdt.assert_frame_equal(actual_data, expected_data)
