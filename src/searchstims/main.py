import argparse
import ast
import configparser
import json
import os

import pygame

import searchstims.make


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
    # config parsing boilerplate
    config = configparser.ConfigParser()
    config.read(args.config)
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
        json_filename = os.path.join(output_dir,
                                     config['config']['json_filename'])
    else:
        json_filename = os.path.join(output_dir,
                                     'filenames_by_set_size_'
                                     'and_target.json')

    # put filenames in a dict that we save as json
    # so we don't have to do a bunch of string matching to find them later,
    # instead we can just get all the filenames for a given set size
    # with target present or absent
    # by using appropriate keys
    # e.g. fnames_set_size_8_target_present = filenames_dict[8]['present']
    filenames_dict = {}
    if stimulus == 'rectangle':
        stim_maker = searchstims.make.RectangleStimMaker()
    elif stimulus == 'number':
        stim_maker = searchstims.make.NumberStimMaker()

    for set_size in set_sizes:
        # add dict for this set size that will have list of "target present / absent" filenames
        filenames_dict[set_size] = {}
        for target in ('present', 'absent'):
            # add the actual filename list for 'present' or 'absent'
            filenames_dict[set_size][target] = []
            if target == 'present':
                inds_of_stim_to_make = range(num_target_present // len(set_sizes))
                num_target = 1
            elif target == 'absent':
                inds_of_stim_to_make = range(num_target_absent // len(set_sizes))
                num_target = 0

            for i in inds_of_stim_to_make:
                if stimulus == 'rectangle':
                    filename = ('redvert_v_greenvert_set_size_{}_'
                                'target_{}_{}.png'.format(set_size, target, i))
                elif stimulus == 'number':
                    filename = ('two_v_five_set_size_{}_'
                                'target_{}_{}.png'.format(set_size, target, i))
                    surface = stim_maker.make_stim(set_size=set_size,
                                                   num_target=num_target)
                filename = os.path.join(output_dir, filename)
                pygame.image.save(surface, filename)
                filenames_dict[set_size][target].append(filename)

    filenames_json = json.dumps(filenames_dict, indent=4)
    with open(json_filename, 'w') as json_output:
        print(filenames_json, file=json_output)

if __name__ == '__main__':
    main()
