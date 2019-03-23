import os
import configparser
from collections import namedtuple
from distutils.util import strtobool
import ast

this_file_dir = os.path.dirname(__file__)

CONFIG_TYPES = configparser.ConfigParser()
CONFIG_TYPES.read(os.path.join(this_file_dir, 'types.ini'))
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
    config_tuple : namedtuple
        where fields are sections of the config, and
        values for those fields are also namedtuples,
        with fields being options and values being the
        values for those options from the config.ini file.
    """
    if config_file and config:
        raise TypeError('cannot call parse function with config_file and config, '
                        'unclear which to use.')

    if config_file:
        if not os.path.isfile(config_file):
            raise FileNotFoundError(f'config_file {config_file} not found')

        config = configparser.ConfigParser()
        config.read(config_file)

    config_sections = config.sections()

    for section in config.sections():
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

    # fancy way of turning ConfigParser instance into a namedtuple
    sections = [key for key in list(config.keys()) if key != 'DEFAULT']
    ConfigTuple = namedtuple('ConfigTuple', sections)
    config_dict = {}
    for section in sections:
        section_keys = list(config[section].keys())
        section_values = list(config[section].values())
        SubTup = namedtuple(section, section_keys)
        subtup_dict = {}
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

            subtup_dict[key] = typed_val
        config_dict[section] = SubTup(**subtup_dict)
    config_tuple = ConfigTuple(**config_dict)
    return config_tuple
