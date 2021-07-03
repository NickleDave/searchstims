import os


CONSOLE_SCRIPT_NAME = 'searchstims'


def test_console_script_help():
    exit_status = os.system(f'{CONSOLE_SCRIPT_NAME} --help')
    assert exit_status == 0


def test_console_script(two_v_five_config_path):
    exit_status = os.system(f'{CONSOLE_SCRIPT_NAME} {two_v_five_config_path}')
    assert exit_status == 0
