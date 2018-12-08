import os
import configparser
from collections import namedtuple
from distutils.util import strtobool
import ast

this_file_dir = os.path.dirname(__file__)

config_types = configparser.ConfigParser()
config_types.read(os.path.join(this_file_dir, 'types.ini'))


def parse(config=None):
    """read config.ini file with config parser,
    returns namedtuple ConfigTuple with
    sections and options as attributes.

    Parameters
    ----------
    config : str
        Path to a config.ini file. If None, the
        default configuration is returned.
        Default is None.

    Returns
    -------
    config : namedtuple
        where fields are sections of the config, and
        values for those fields are also namedtuples,
        with fields being options and values being the
        values for those options from the config.ini file.
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    if config.has_option(section='config',
                         option='output_dir'):
        output_dir = config['config']['output_dir']
        config['config']['output_dir'] = os.path.expanduser(output_dir)
    else:
        config['config']['output_dir'] = os.path.join('.', 'output')

    if config.has_option(section='config',
                         option='json_filename'):
        if os.path.split(config['config']['json_filename'])[0] == '':
            config['config']['json_filename'] = os.path.join(output_dir,
                                                             config['config']['json_filename'])
        else:
            config['config']['json_filename'] = config['config']['json_filename']
    else:
        # default filename if option not used
        config['config']['json_filename'] = os.path.join(output_dir,
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
            val_type = config_types[section][key]
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
