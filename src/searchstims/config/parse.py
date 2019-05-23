import os
import configparser
from distutils.util import strtobool
import ast

from .classes import Config, GeneralConfig, RVvGVConfig, Two_v_Five_Config

SECTION_CONFIG_ATTRIB_MAP = {
    'general': 'general',
    'RVvGV': 'RVvGV',
    '2_v_5': 'Two_v_Five',
}


SECTION_CLASS_MAP = {
    'general': GeneralConfig,
    'RVvGV': RVvGVConfig,
    '2_v_5': Two_v_Five_Config,
}


this_file_dir = os.path.dirname(__file__)

CONFIG_TYPES = configparser.ConfigParser()
CONFIG_TYPES.read(os.path.join(this_file_dir, 'types.ini'))
VALID_SECTIONS = CONFIG_TYPES.sections()

DEFAULT_CONFIG = configparser.ConfigParser()
DEFAULT_CONFIG.read(os.path.join(this_file_dir, 'default.ini'))


def parse(config_file=None):
    """read config.ini file with config parser,
    returns namedtuple ConfigTuple with
    sections and options as attributes.

    Parameters
    ----------
    config_file : str
        Path to a config.ini file. If None, the default configuration is returned.
        Default is None.

    Returns
    -------
    config : searchstims.config.classes.Config
        instance of Config class that represents sections of config.ini file,
        with attributes general, number, and rectangle, each of which is an
        instance of a class that represents those sections with attributes being
        the options in those sections and the corresponding values set by the
        user.
    """
    if not os.path.isfile(config_file):
        raise FileNotFoundError(f'config_file {config_file} not found')

    config = configparser.ConfigParser()
    config.read(config_file)

    if not config.has_section('general'):
        raise ValueError(
            f"'general' section required in configuration file but not found in {config_file}"
        )

    # validate sections and set default values from default.ini
    for section in config.sections():
        # is section name valid?
        if section not in VALID_SECTIONS:
            raise ValueError(f'invalid section name: {section}.\n'
                             f'Valid section names are: {VALID_SECTIONS}')
        # if so, check for undeclared options and if not declared, set to defaults from default.ini
        for option in DEFAULT_CONFIG.options(section):
            if not config.has_option(section, option):
                config[section][option] = DEFAULT_CONFIG[section][option]

    if config.has_option(section='general',
                         option='output_dir'):
        output_dir = config['general']['output_dir']
        config['general']['output_dir'] = os.path.expanduser(output_dir)

    sections = [key for key in list(config.keys()) if key != 'DEFAULT']
    typed_config_dict = {}
    for section in sections:
        section_keys = list(config[section].keys())
        section_values = list(config[section].values())
        section_dict = {}
        for key, val in zip(section_keys, section_values):
            if val == 'None':
                typed_val = None
            else:
                val_type = CONFIG_TYPES[section][key]
                if val_type == 'int':
                    typed_val = int(val)
                elif val_type == 'float':
                    typed_val = float(val)
                elif val_type == 'bool':
                    typed_val = bool(strtobool(val))
                elif val_type == 'list' or val_type == 'tuple':
                    typed_val = ast.literal_eval(val)
                elif val_type == 'str':
                    typed_val = val
            section_dict[key] = typed_val
        typed_config_dict[section] = section_dict

    # if user didn't declare some stim section, set to None
    for section in VALID_SECTIONS:
        if section not in typed_config_dict:
            typed_config_dict[section] = None

    config_classes_dict = {}
    for section in typed_config_dict.keys():
        if typed_config_dict[section] is not None:
            section_attrib = SECTION_CONFIG_ATTRIB_MAP[section]
            section_class = SECTION_CLASS_MAP[section]
            config_classes_dict[section_attrib] = section_class(**typed_config_dict[section])

    config_obj = Config(**config_classes_dict)

    return config_obj
