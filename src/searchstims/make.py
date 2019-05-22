import os
import json
from math import ceil
import random
from itertools import combinations, product

import numpy as np
import pygame

from .stim_makers import AbstractStimMaker


def _generate_xx_and_yy(set_size, num_imgs, stim_maker):
    # get all combinations of cells (combination because order doesn't matter, just which cells get used)
    # a cell combination is an unordered set of k cells from a grid with a total of n cells
    # e.g. if there are 25 cells in a 5x5 grid and you want all combinations k=1, then the
    # cell_combs will be [(0,), (1,), (2,), ... (24,)] (representing each as a tuple)
    # and all combinations k=2 will be [(0,1), (0,2), (0,3), ... (1,2), (1,3), ... (23, 24)]
    # (there are no repeats; once we draw a cell we don't replace it since we just put one item in each cell)
    cell_combs = list(combinations(iterable=range(stim_maker.num_cells), r=set_size))
    if len(cell_combs) < num_imgs:
        num_repeat = ceil(num_imgs / len(cell_combs))
        make_jitter_unique = True
    else:
        # don't need to repeat any cell combinations; let's just sample without replacement
        all_cells_to_use = random.sample(population=cell_combs, k=num_imgs)
        num_repeat = 0
        make_jitter_unique = False

    # if jitter > 0, compute 'jitter_range'
    # (vector of possible jitter amounts within maximum jitter from which to draw randomly)
    if stim_maker.jitter > 0:
        jitter_high = stim_maker.jitter // 2
        jitter_low = -jitter_high
        if stim_maker.jitter % 2 == 0:  # if even
            # have to account for zero at center of jitter range
            # (otherwise range would be jitter + 1)
            # (Not a problem when doing floor division on odd #s)
            coin_flip = np.random.choice([0, 1])
            if coin_flip == 0:
                jitter_low += 1
            elif coin_flip == 1:
                jitter_high -= 1
        jitter_range = range(jitter_low, jitter_high + 1)
        # get cartesian product of jitter range of length 2, i.e. all x-y co-ordinates
        # here we want cartesian product because order does matter, jitter of (1,0) != (0, 1)
        # and because we want repeats, e.g. (2, 2)
        jitter_product = list(product(jitter_range, repeat=2))

        if make_jitter_unique:
            # get each unique pairing of possible cell combinations and possible x, y jitters
            cell_jitter_prod = list(product(cell_combs, jitter_product))
            if len(cell_jitter_prod) < num_imgs:
                raise ValueError('cannot generate unique x and y co-ordinates for items in number of images specified; '
                                 f'the product of the number of cell combinations {len(all_cells_to_use)} and the '
                                 f'possible jitter added {len(jitter_product)} is {len(cell_jitter_prod)}, but '
                                 f'the number of images to generate is {num_imgs}')
            else:
                cell_and_jitter = []
                for this_cell_comb in cell_combs:
                    this_cell_comb_with_all_jitter = [cell_jitter_tuple
                                                      for cell_jitter_tuple in cell_jitter_prod
                                                      if cell_jitter_tuple[0] == this_cell_comb]
                    this_cell_comb_with_jitter = random.sample(population=this_cell_comb_with_all_jitter,
                                                               k=num_repeat)
                    cell_and_jitter.extend(this_cell_comb_with_jitter)
                diff = len(cell_and_jitter) - num_imgs
                # remove extras randomly instead of removing all from the last cell_comb
                inds_to_remove = random.sample(range(len(cell_and_jitter)), k=diff)
                inds_to_remove.sort(reverse=True)
                for ind in inds_to_remove:
                    cell_and_jitter.pop(ind)
                all_cells_to_use = [cj_tup[0] for cj_tup in cell_and_jitter]
        else:
            jitter_rand = random.choices(jitter_product, k=len(all_cells_to_use))
            cell_and_jitter = zip(all_cells_to_use, jitter_rand)
    else:
        jitter_none = [None] * len(all_cells_to_use)
        cell_and_jitter = zip(all_cells_to_use, jitter_none)

    ###########################################################################
    # notice: below we always refer to y before x, because shapes are         #
    # specified in order of (height, width). So size[0] = y and size[1] = x   #
    ###########################################################################
    all_yy_to_use_ctr = []
    all_xx_to_use_ctr = []
    for cells_to_use, jitter_to_add in cell_and_jitter:
        # need to cast to list and then array because converting a list with asarray returns a 1-dimensional
        # array, and indexing with this one-dimensional array returns another 1-d array. Using just a tuple
        # or an array made from a tuple will just return a single element when the tuple has only one element,
        # and this will raise an error when that one element is passed to stim_maker instead of a 1-d, 1 element
        # array
        cells_to_use = np.asarray(list(cells_to_use))
        yy_to_use = stim_maker.yy[cells_to_use]
        xx_to_use = stim_maker.xx[cells_to_use]

        # find centers of cells we're going to use
        yy_to_use_ctr = (yy_to_use * stim_maker.cell_height) - stim_maker.cell_y_center
        xx_to_use_ctr = (xx_to_use * stim_maker.cell_width) - stim_maker.cell_x_center

        if stim_maker.border_size:
            yy_to_use_ctr += round(stim_maker.border_size[0] / 2)
            xx_to_use_ctr += round(stim_maker.border_size[1] / 2)

        if jitter_to_add:
            yy_to_use_ctr += jitter_to_add[0]
            xx_to_use_ctr += jitter_to_add[1]

        all_yy_to_use_ctr.append(yy_to_use_ctr)
        all_xx_to_use_ctr.append(xx_to_use_ctr)

    return all_cells_to_use, all_xx_to_use_ctr, all_yy_to_use_ctr


def make(root_output_dir,
         stim_dict,
         json_filename,
         num_target_present,
         num_target_absent,
         set_sizes):
    """make visual search stimuli given an output directory and a set of StimMaker classes

    Parameters
    ----------

    Returns
    -------
    None

    saves all the stimuli to config_obj.output_dir, and saves information about
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
    for stim_name, stim_maker in stim_dict.items():
        if type(stim_name) != str:
            raise TypeError(
                f'all keys in stim_dict must be strings but found key of type {type(stim_name)}'
            )
        if not issubclass(type(stim_maker), AbstractStimMaker):
            raise TypeError(
                f'stim_maker not recognized as a subclass of AbstractStimMaker, type was {stim_maker}'
            )

    if not os.path.isdir(root_output_dir):
        os.makedirs(root_output_dir)

    # put filenames and other info in a dict that we serialize as json
    # so we don't have to do a bunch of string matching to find filenames later,
    # instead we just load back into Python as a dict 
    # and can just get all the filenames for a given set size with target present or absent
    # by using appropriate keys
    # e.g. fnames_set_size_8_target_present = [stim_info['filename'] for stim_info in out_dict[8]['present']]
    metadata = {}

    for stim_name, stim_maker in stim_dict.items():

            this_stim_name_output_dir = os.path.join(root_output_dir, stim_name)

            metadata[stim_name] = {}

            num_imgs_present = num_target_present // len(set_sizes)
            num_imgs_absent = num_target_absent // len(set_sizes)

            for set_size in set_sizes:
                # add dict for this set size that will have list of "target present / absent" filenames
                metadata[stim_name][set_size] = {}

                if not os.path.isdir(
                    os.path.join(this_stim_name_output_dir, str(set_size))
                ):
                    os.makedirs(
                        os.path.join(this_stim_name_output_dir, str(set_size))
                    )

                for target in ('present', 'absent'):
                    # add the actual filename list for 'present' or 'absent'
                    metadata[stim_name][set_size][target] = []
                    if target == 'present':
                        img_nums = list(range(num_imgs_present))
                        num_target = 1
                    elif target == 'absent':
                        img_nums = list(range(num_imgs_absent))
                        num_target = 0

                    if not os.path.isdir(
                            os.path.join(this_stim_name_output_dir, str(set_size), target)
                    ):
                        os.makedirs(os.path.join(this_stim_name_output_dir, str(set_size), target))

                    all_cells_to_use, all_xx_to_use_ctr, all_yy_to_use_ctr = _generate_xx_and_yy(set_size=set_size,
                                                                                                 num_imgs=len(img_nums),
                                                                                                 stim_maker=stim_maker)

                    for img_num, cells_to_use, xx_to_use_ctr, yy_to_use_ctr in zip(img_nums,
                                                                                   all_cells_to_use,
                                                                                   all_xx_to_use_ctr,
                                                                                   all_yy_to_use_ctr):
                        rect_tuple = stim_maker.make_stim(set_size=set_size,
                                                          num_target=num_target,
                                                          cells_to_use=cells_to_use,
                                                          xx_to_use_ctr=xx_to_use_ctr,
                                                          yy_to_use_ctr=yy_to_use_ctr)

                        filename = (
                            f'{stim_name}_set_size_{set_size}_target_{target}_{img_num}.png'
                        )

                        # use absolute path to save
                        absolute_path_filename = os.path.join(this_stim_name_output_dir,
                                                              str(set_size),
                                                              target,
                                                              filename)
                        pygame.image.save(rect_tuple.display_surface, absolute_path_filename)
                        # use relative path for name of file in .json
                        # so it won't break anything if we move the whole directory of images around;
                        # --> it's the job of code the images to know where directory is at
                        relative_path_filename = os.path.join(stim_name, str(set_size), target, filename)
                        stim_info = {
                            'filename': relative_path_filename,
                            'grid_as_char': rect_tuple.grid_as_char,
                            'target_indices': rect_tuple.target_indices,
                            'distractor_indices': rect_tuple.distractor_indices,
                        }
                        metadata[stim_name][set_size][target].append(stim_info)

    metadata_json = json.dumps(metadata, indent=4)
    json_filename = os.path.expanduser(json_filename)
    if os.path.split(json_filename)[0] == '':
        json_filename = os.path.join(root_output_dir, json_filename)

    with open(json_filename, 'w') as json_fp:
        print(metadata_json, file=json_fp)
