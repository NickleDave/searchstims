from pathlib import Path

import pytest

HERE = Path(__file__).parent


@pytest.fixture
def data_for_tests_root():
    return HERE / '..' / 'test_data'
