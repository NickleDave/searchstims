import os
import json
import pygame

from . import stim_makers


def make(config_tuple):
    """actual function that makes all the stimuli

    Parameters
    ----------
    config_tuple : ConfigTuple
        returned by parse_config after parsing a config.ini file

    Returns
    -------
    None

    saves all the stimuli to config_tuple.output_dir, and saves information about
    stimuli in a .json output file. This .json file is a serialized Python
    dictionary of dictionaries with the following key, field pairs:
    {set size: {
        'present': [
            {'filename': str,
             'grid_as_char': list,
            ]

    Keys at the top level are set size, the total number of targets and distractors, e.g.,
    {1, 2, ..., 8}. Each set size key has as its value another dictionary,
    whose keys are 'present' and 'absent', referring to the visual search target.
    Each 'present' and 'absent' key has as its value a list of Python dictionaries;
    each dictionary in the list has info about the actual visual search stimulus image
    that it corresponds to:
        filename: str
            actual visual search stimulus filename
        grid_as_char: list
            of list of str. Representation of stimulus as a grid of
            cells
        target_indices: list
            of two-element lists, the x and y co-ordinates for the
            center of the targets (or indices if you load the image into
            an array).
        distractor_indices: list
            of two-element lists, the x and y co-ordinates for the
            center of the distractors (or indices if you load the image into
            an array).

    Here is an excerpt from such a file:
        {'1': {'absent': [{'distractor_indices': [[203, 65]],
            'filename': '/home/user/output/1/absent/redvert_v_greenvert_set_size_1_target_absent_0.png',
            'grid_as_char':
                [['', '', '', '', ''],
                 ['', '', '', '', 'd'],
                 ['', '', '', '', ''],
                 ['', '', '', '', ''],
                 ['', '', '', '', '']],
            'target_indices': []},
           {'distractor_indices': [[111, 21]],
            'filename': '/home/user/output/1/absent/redvert_v_greenvert_set_size_1_target_absent_1.png',
            ...
         '2': {'absent': [{'distractor_indices': [[68, 22], [65, 204]],
            'filename': '/home/user/output/2/absent/redvert_v_greenvert_set_size_2_target_absent_0.png',
            'grid_as_char': [['', 'd', '', '', ''],
            ...
    """
    if not os.path.isdir(config_tuple.general.output_dir):
        os.makedirs(config_tuple.general.output_dir)
    # put filenames in a dict that we save as json
    # so we don't have to do a bunch of string matching to find them later,
    # instead we can just get all the filenames for a given set size
    # with target present or absent
    # by using appropriate keys
    # e.g. fnames_set_size_8_target_present = filenames_dict[8]['present']
    filenames_dict = {}

    if hasattr(config_tuple, 'rectangle'):
        init_config = config_tuple.rectangle
        stim_maker = stim_makers.RectangleStimMaker(target_color=init_config.target_color,
                                                    distractor_color=init_config.distractor_color,
                                                    window_size=init_config.image_size,
                                                    grid_size=init_config.grid_size,
                                                    rects_width_height=init_config.rects_width_height,
                                                    jitter=init_config.jitter
                                                    )
    elif hasattr(config_tuple, 'number'):
        init_config = config_tuple.number
        stim_maker = stim_makers.NumberStimMaker(target_color=init_config.target_color,
                                                 distractor_color=init_config.distractor_color,
                                                 window_size=init_config.image_size,
                                                 grid_size=init_config.grid_size,
                                                 rects_width_height=init_config.rects_width_height,
                                                 jitter=init_config.jitter,
                                                 target_number=init_config.target_number,
                                                 distractor_number=init_config.distractor_number
                                                 )

    general_config = config_tuple.general
    for set_size in general_config.set_sizes:
        # add dict for this set size that will have list of "target present / absent" filenames
        filenames_dict[set_size] = {}

        if not os.path.isdir(
            os.path.join(general_config.output_dir, str(set_size))
        ):
            os.makedirs(
                os.path.join(general_config.output_dir, str(set_size))
            )
        for target in ('present', 'absent'):
            # add the actual filename list for 'present' or 'absent'
            filenames_dict[set_size][target] = []
            if target == 'present':
                inds_of_stim_to_make = range(general_config.num_target_present // len(general_config.set_sizes))
                num_target = 1
            elif target == 'absent':
                inds_of_stim_to_make = range(general_config.num_target_absent // len(general_config.set_sizes))
                num_target = 0

            if not os.path.isdir(
                    os.path.join(general_config.output_dir, str(set_size), target)
            ):
                os.makedirs(os.path.join(general_config.output_dir, str(set_size), target))

            for i in inds_of_stim_to_make:
                rect_tuple = stim_maker.make_stim(set_size=set_size,
                                                  num_target=num_target)
                if hasattr(config_tuple, 'rectangle'):
                    filename = ('redvert_v_greenvert_set_size_{}_'
                                'target_{}_{}.png'.format(set_size, target, i))
                elif hasattr(config_tuple, 'number'):
                    filename = ('two_v_five_set_size_{}_'
                                'target_{}_{}.png'.format(set_size, target, i))
                filename = os.path.join(general_config.output_dir,
                                        str(set_size),
                                        target,
                                        filename)
                pygame.image.save(rect_tuple.display_surface, filename)
                file_dict = {
                    'filename': filename,
                    'grid_as_char': rect_tuple.grid_as_char,
                    'target_indices': rect_tuple.target_indices,
                    'distractor_indices': rect_tuple.distractor_indices,
                }
                filenames_dict[set_size][target].append(file_dict)

    filenames_json = json.dumps(filenames_dict, indent=4)
    json_filename = os.path.expanduser(general_config.json_filename)
    with open(json_filename, 'w') as json_output:
        print(filenames_json, file=json_output)
