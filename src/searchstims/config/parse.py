import os
import configparser
from distutils.util import strtobool
import ast

from .classes import Config, GeneralConfig, RectangleConfig, NumberConfig

SECTION_CLASS_MAP = {
    'general': GeneralConfig,
    'rectangle': RectangleConfig,
    'number': NumberConfig,
}


this_file_dir = os.path.dirname(__file__)

CONFIG_TYPES = configparser.ConfigParser()
CONFIG_TYPES.read(os.path.join(this_file_dir, 'types.ini'))
VALID_SECTIONS = CONFIG_TYPES.sections()

DEFAULT_CONFIG = configparser.ConfigParser()
DEFAULT_CONFIG.read(os.path.join(this_file_dir, 'default.ini'))


def parse(config_file=None, config=None):
    """read config.ini file with config parser,
    returns namedtuple ConfigTuple with
    sections and options as attributes.

    Parameters
    ----------
    config_file : str
        Path to a config.ini file. If None, the
        default configuration is returned.
        Default is None.
    config: configparser.ConfigParser
        instance of ConfigParser that already has sections and options declared.
        This parameter is mainly used in testing, to write tests where the options
        are explicit in that file.

    Returns
    -------
    config : searchstims.config.classes.Config
        instance of Config class that represents sections of config.ini file,
        with attributes general, number, and rectangle, each of which is an
        instance of a class that represents those sections with attributes being
        the options in those sections and the corresponding values set by the
        user.
    """
    if config_file and config:
        raise TypeError('cannot call parse function with config_file and config, '
                        'unclear which to use.')

    if config_file:
        if not os.path.isfile(config_file):
            raise FileNotFoundError(f'config_file {config_file} not found')

        config = configparser.ConfigParser()
        config.read(config_file)

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
    else:
        config['general']['output_dir'] = os.path.join('.', 'output')

    if config.has_option(section='general',
                         option='json_filename'):
        if os.path.split(config['general']['json_filename'])[0] == '':
            config['general']['json_filename'] = os.path.join(output_dir,
                                                             config['general']['json_filename'])
        else:
            config['general']['json_filename'] = config['general']['json_filename']
    else:
        # default filename if option not used
        config['general']['json_filename'] = os.path.join(output_dir,
                                                          'filenames_by_set_size_'
                                                          'and_target.json')

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
        if section not in config_dict:
            config_dict[section] = None

    config_classes_dict = {}
    for section in config_dict.keys():
        if section is not None:
            section_class = SECTION_CLASS_MAP[section]
            config_classes_dict[section] = section_class(**typed_config_dict)

    config_obj = Config(**config_classes_dict)

    return config_obj
