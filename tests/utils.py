from pathlib import Path

TEST_PATH = Path(__file__).parent
FIXTURES_PATH = TEST_PATH / 'fixtures'


def print_frame_differing_rows(df1, df2):
    """Print the difference between two :class:`DataFrame`s

    Prints the rows of the two DataFrames which differ, along with a
    boolean DataFrame indicating which individual values differ.

    Args:
        df1, df2 (:class:`pandas.DataFrame`): The two DataFrames to
            compare.
    """
    diff = (df1 == df2) | df1.isnull() | df2.isnull()
    rows = ~(diff.all(axis=1))
    print(df1[rows])
    print(df2[rows])
    print(diff[rows])
