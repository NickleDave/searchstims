import pytest


@pytest.fixture
def configs_root(data_for_tests_root):
    return data_for_tests_root / 'configs'


@pytest.fixture
def two_v_five_config_path(configs_root):
    return configs_root / 'test_2_v_5_config.ini'
