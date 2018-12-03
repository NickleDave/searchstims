import argparse
import ast
import configparser
import json
import os
from typing import NamedTuple

import pygame

from . import stim_makers


class ConfigTuple(NamedTuple):
    """represent config"""
    num_target_present: int
    num_target_absent: int
    set_sizes: list
    stimulus: str
    output_dir: str
    json_filename: str


def parse_config(config_file):
    """parse config; convert strings to correct types

    Parameters
    ----------
    config_file : str
        filename of a config.ini file

    Returns
    -------
    config_tuple : ConfigTuple
        with fields
            num_target_present: int
            num_target_absent: int
            set_sizes: list
            stimulus: str
            output_dir: str
            json_filename: str
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    num_target_present = int(config['config']['num_target_present'])
    num_target_absent = int(config['config']['num_target_absent'])
    set_sizes = ast.literal_eval(config['config']['set_sizes'])
    stimulus = config['config']['stimulus']
    if config.has_option(section='config',
                         option='output_dir'):
        output_dir = config['config']['output_dir']
        output_dir = os.path.expanduser(output_dir)
    else:
        output_dir = os.path.join('.', 'output')

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    if config.has_option(section='config',
                         option='json_filename'):
        if os.path.split(config['config']['json_filename'])[0] == '':
            json_filename = os.path.join(output_dir,
                                         config['config']['json_filename'])
        else:
            json_filename = config['config']['json_filename']
    else:
        # default filename if option not used
        json_filename = os.path.join(output_dir,
                                     'filenames_by_set_size_'
                                     'and_target.json')
    return ConfigTuple(num_target_present,
                       num_target_absent,
                       set_sizes,
                       stimulus,
                       output_dir,
                       json_filename
                       )


def make(config_tuple):
    """actual function that makes all the stimuli

    Parameters
    ----------
    config_tuple : ConfigTuple
        returned by parse_config after parsing a config.ini file

    Returns
    -------
    None

    saves all the stimuli to config_tuple.output_dir
    """
    # put filenames in a dict that we save as json
    # so we don't have to do a bunch of string matching to find them later,
    # instead we can just get all the filenames for a given set size
    # with target present or absent
    # by using appropriate keys
    # e.g. fnames_set_size_8_target_present = filenames_dict[8]['present']
    filenames_dict = {}
    if config_tuple.stimulus == 'rectangle':
        stim_maker = stim_makers.RectangleStimMaker()
    elif config_tuple.stimulus == 'number':
        stim_maker = stim_makers.NumberStimMaker()

    for set_size in config_tuple.set_sizes:
        # add dict for this set size that will have list of "target present / absent" filenames
        filenames_dict[set_size] = {}

        if not os.path.isdir(
            os.path.join(config_tuple.output_dir, str(set_size))
        ):
            os.makedirs(
                os.path.join(config_tuple.output_dir, str(set_size))
            )
        for target in ('present', 'absent'):
            # add the actual filename list for 'present' or 'absent'
            filenames_dict[set_size][target] = []
            if target == 'present':
                inds_of_stim_to_make = range(config_tuple.num_target_present // len(config_tuple.set_sizes))
                num_target = 1
            elif target == 'absent':
                inds_of_stim_to_make = range(config_tuple.num_target_absent // len(config_tuple.set_sizes))
                num_target = 0

            if not os.path.isdir(
                    os.path.join(config_tuple.output_dir, str(set_size), target)
            ):
                os.makedirs(os.path.join(config_tuple.output_dir, str(set_size), target))

            for i in inds_of_stim_to_make:
                if config_tuple.stimulus == 'rectangle':
                    filename = ('redvert_v_greenvert_set_size_{}_'
                                'target_{}_{}.png'.format(set_size, target, i))
                elif config_tuple.stimulus == 'number':
                    filename = ('two_v_five_set_size_{}_'
                                'target_{}_{}.png'.format(set_size, target, i))
                surface = stim_maker.make_stim(set_size=set_size,
                                               num_target=num_target)
                filename = os.path.join(config_tuple.output_dir,
                                        str(set_size),
                                        target,
                                        filename)
                pygame.image.save(surface, filename)
                filenames_dict[set_size][target].append(filename)

    filenames_json = json.dumps(filenames_dict, indent=4)
    with open(config_tuple.json_filename, 'w') as json_output:
        print(filenames_json, file=json_output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config',
                        type=str,
                        help=('filename of config file. '
                              'For an example config.ini file, see: '
                              'https://github.com/NickleDave/searchstims'))
    args = parser.parse_args()
    config_file = args.config
    if not os.path.isfile(config_file):
        raise FileNotFoundError("Config file {} not found".format(config_file))
    config_tuple = parse_config(config_file)
    make(config_tuple)


if __name__ == '__main__':
    main()
