from itertools import combinations, product
import json
from math import ceil
from pathlib import Path
import random

import numpy as np
import pygame

from .stim_makers import AbstractStimMaker
from .utils import make_csv


def _generate_xx_and_yy(set_size,
                        num_imgs,
                        stim_maker):
    """helper function that computes x,y co-ordinates for items in visual search stimulus

    ensures that there are no repeated images in dataset

    finds number of combinations of cells given set size of stimulus and grid size specified for it
    """
    # get all combinations of cells (combination because order doesn't matter, just which cells get used)
    # a cell combination is an unordered set of k cells from a grid with a total of n cells
    # e.g. if there are 25 cells in a 5x5 grid and you want all combinations k=1, then the
    # cell_combs will be [(0,), (1,), (2,), ... (24,)] (representing each as a tuple)
    # and all combinations k=2 will be [(0,1), (0,2), (0,3), ... (1,2), (1,3), ... (23, 24)]
    # (there are no repeats; once we draw a cell we don't replace it since we just put one item in each cell)
    cell_combs = list(combinations(iterable=range(stim_maker.num_cells), r=set_size))

    # if there are less combinations then there are number of images, we need to make sure we make jitter
    # unique so we don't get any repeat images
    if len(cell_combs) < num_imgs:
        # num_repeat: maximum number of times we might use any given cell combination
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
        jitter_coords = list(product(jitter_range, repeat=2))

        if make_jitter_unique:
            # get each unique pairing of possible cell combinations and possible x, y jitters
            if len(cell_combs) * len(jitter_coords) < num_imgs:
                raise ValueError('cannot generate unique x and y co-ordinates for items in number of images specified; '
                                 f'the product of the number of cell combinations {len(all_cells_to_use)} and the '
                                 f'possible jitter added {len(jitter_coords)} is {len(cell_combs) * len(jitter_coords)}'
                                 f', but the number of images to generate is {num_imgs}')
            else:
                cell_and_jitter = []
                for this_cell_comb in cell_combs:
                    jitter_sample = random.sample(population=jitter_coords, k=num_repeat)
                    this_cell_comb_with_jitter = [(this_cell_comb, jitter_coord_tup)
                                                  for jitter_coord_tup in jitter_sample]
                    cell_and_jitter.extend(this_cell_comb_with_jitter)
                diff = len(cell_and_jitter) - num_imgs
                # remove extras randomly instead of removing all from the last cell_comb
                inds_to_remove = random.sample(range(len(cell_and_jitter)), k=diff)
                inds_to_remove.sort(reverse=True)
                for ind in inds_to_remove:
                    cell_and_jitter.pop(ind)
                all_cells_to_use = [cj_tup[0] for cj_tup in cell_and_jitter]
        else:
            jitter_rand = random.choices(jitter_coords, k=len(all_cells_to_use))
            cell_and_jitter = zip(all_cells_to_use, jitter_rand)
    else:  # if jitter == 0
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
         csv_filename,
         num_target_present,
         num_target_absent,
         set_sizes):
    """make visual search stimuli given an output directory and a set of StimMaker classes

    Parameters
    ----------
    root_output_dir : str, Path
        directory in which output should be saved
    stim_dict : dict
        key, value pairs where the key is the visual search stimulus name and the 'value' is
        an instance of a StimMaker
    csv_filename : str
        name for .csv file that will be saved containing metadata about generated set of images (see Notes below).
    num_target_present : int, list
        number of visual search stimuli to generate with target present.
        If int, the number of stimuli generated for each set size will be num_target_present // len(set_sizes).
        List should be same length as set_sizes with an int value for each set size, the number of 'target present'
        images to make for that set size.
    num_target_absent : int, list
        number of visual search stimuli to generate with target absent.
        If int, the number of stimuli generated for each set size will be num_target_absent // len(set_sizes).
        List should be same length as set_sizes with an int value for each set size, the number of 'target absent'
        images to make for that set size.
    set_sizes : list
        of int, e.g. [1, 2, 4, 8]. If num_target_present and num_target_absent are ints, not lists, then
        the number of stimuli generated for each set size will be num_target_present(absent) // len(set_size).
        E.g., 4800 / 4 = 1200 images per set size. If num_target_present/absent are lists then each should
        be the same length as set_sizes and the value at the index corresponding to each set size determines the
        number of stimuli generated for that set size. E.g. if num_target_present = [1000, 2000, 4000] and
        set_sizes = [1, 2, 4] then there will be 1000 stimuli with set size 1, 2000 with set size 2, and 4000
        with set size 4.

    Returns
    -------
    None

    Notes
    -----
    This function saves all the stimuli to root_output_dir, and saves information about
    stimuli in a .csv output file. The .csv file has the following fields:
        stimulus : str
            name of visual search stimulus, e.g. 'RVvGV'.
        set_size : int
            visual search set size, i.e. total number of targets and distractors
            in the stimulus.
        target_condition : str
            one of {'present', 'absent'}. Whether stimulus contains target.
        img_num : int
            a unique index assigned to the image by the main loop that creates them.
            Makes it possible to distinguish multiple images that would otherwise have
            the same filename (e.g. because they both have set size of 8 and target
            present, but the items are in different locations).
        root_output_dir : str
            location specified by user where all images are saved
        img_file : str
            relative path to image from root_output_dir.
            So the following produces the absolute path:
            >>> Path(root_output_dir).joinpath(img_file)
        meta_file : str
            relative path to .json metadata file associated with the image.
            The metadata file contains the indices of the centers of items
            in the image, i.e. their location. If the images were generated
            using a grid (instead of randomly placing items) then the metadata
            will also contain a string representation of where items are in the
            grid. This string representation can be used to find e.g. all stimuli
            of set size 8 where the target was on the left side of the image.

    The .json metadata files are Python dictionaries with the following key/value pairs:
        img_filename : str
            name of image file that metadata is associated with.
            Included in metadata so user does not have to extract it from filename.
        target_indices : list
            co-ordinates of targets, i.e. indices in array representing image.
            A Numpy array converted to a list.
        distractor_indices : list
            co-ordinates of distractors, i.e. indices in array representing image
            A Numpy array converted to a list.
        grid_as_char : str
            Representation of stimulus as characters. This is only added when the stimulus
            is generated as a grid where the items can appear within cells on the grid.
            If the stimulus is generated with another method, e.g. randomly placing items,
            then the value for this key will be None.

    Here is an example dictionary from a metadata file:
    {'img_filename': 'RVvGV/1/absent/redvert_v_greenvert_set_size_1_target_absent_0.png',
     'target_indices': [],
     'distractor_indices': [[203, 65]],
     'grid_as_char':
            [['', '', '', '', ''],
             ['', '', '', '', 'd'],
             ['', '', '', '', ''],
             ['', '', '', '', ''],
             ['', '', '', '', '']],
    }
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

    if type(num_target_present) not in (int, list):
        raise TypeError(
            f'num_target_present should be int or list but type was: {type(num_target_present)}'
        )

    if type(num_target_present) is list:
        if len(num_target_present) != len(set_sizes):
            raise ValueError(
                'num_target_present must be same length as set_sizes'
            )

        if not all([type(num) is int for num in num_target_present]):
            raise ValueError(
                'all values in num_target_present should be int'
            )

    if type(num_target_absent) not in (int, list):
        raise TypeError(
            f'num_target_present should be int or list but type was: {type(num_target_absent)}'
        )

    if type(num_target_absent) is list:
        if len(num_target_absent) != len(set_sizes):
            raise ValueError(
                'num_target_absent must be same length as set_sizes'
            )

        if not all([type(num) is int for num in num_target_absent]):
            raise ValueError(
                'all values in num_target_absent should be int'
            )

    if type(root_output_dir) == str:
        root_output_dir = Path(root_output_dir)

    if not root_output_dir.is_dir():
        root_output_dir.mkdir(parents=True)

    # for csv
    rows = []

    for stimulus, stim_maker in stim_dict.items():
        stimulus_output_dir = root_output_dir.joinpath(stimulus)
        if not stimulus_output_dir.is_dir():
            stimulus_output_dir.mkdir()

        # if num_target_present/absent are int, make into list
        # so we can zip them with set_sizes in main loop
        if type(num_target_present) is int:
            num_target_present = num_target_present // len(set_sizes)
            num_target_present = [num_target_present for _ in range(len(set_sizes))]

        if type(num_target_absent) is int:
            num_target_absent = num_target_absent // len(set_sizes)
            num_target_absent = [num_target_absent for _ in range(len(set_sizes))]

        for set_size, num_imgs_present, num_imgs_absent in zip(
                set_sizes, num_target_present, num_target_absent):

            set_size_dir = stimulus_output_dir.joinpath(str(set_size))
            if not set_size_dir.is_dir():
                set_size_dir.mkdir()

            for target_condition in ('present', 'absent'):
                if target_condition == 'present':
                    img_nums = list(range(num_imgs_present))
                    num_target = 1
                elif target_condition == 'absent':
                    img_nums = list(range(num_imgs_absent))
                    num_target = 0

                target_condition_dir = set_size_dir.joinpath(target_condition)
                if not target_condition_dir.is_dir():
                    target_condition_dir.mkdir()

                def _make_stim(img_num, cells_to_use=None,
                               xx_to_use_ctr=None, yy_to_use_ctr=None):
                    """helper function to make and save individual stim

                    Define as a nested function so we can avoid repeating ourselves below
                    """
                    rect_tuple = stim_maker.make_stim(set_size=set_size,
                                                      num_target=num_target,
                                                      cells_to_use=cells_to_use,
                                                      xx_to_use_ctr=xx_to_use_ctr,
                                                      yy_to_use_ctr=yy_to_use_ctr)

                    filename = (
                        f'{stimulus}_set_size_{set_size}_target_{target_condition}'
                        f'_{img_num}.png'
                    )
                    abs_path_filename = target_condition_dir.joinpath(filename)
                    pygame.image.save(rect_tuple.display_surface,
                                      str(abs_path_filename))
                    # use relative path for name of file in csv
                    # so it won't break anything if we move the whole directory of images
                    # we can just change 'root_output_dir' instead
                    img_file = Path(stimulus).joinpath(str(set_size),
                                                       target_condition,
                                                       filename)
                    meta_file = Path(
                        str(abs_path_filename).replace('.png', '.meta.json')
                    )
                    meta_dict = {
                        'img_file': str(img_file),
                        'target_indices': rect_tuple.target_indices,
                        'distractor_indices': rect_tuple.distractor_indices,
                        'grid_as_char': rect_tuple.grid_as_char,
                    }
                    with open(meta_file, 'w') as fp:
                        json.dump(meta_dict, fp)

                    row = (stimulus,
                           set_size,
                           target_condition,
                           img_num,
                           root_output_dir,
                           img_file,
                           meta_file)
                    rows.append(row)

                if stim_maker.grid_size is None:
                    for img_num in img_nums:
                        _make_stim(img_num)
                else:
                    (all_cells_to_use,
                     all_xx_to_use_ctr,
                     all_yy_to_use_ctr) = _generate_xx_and_yy(set_size=set_size,
                                                              num_imgs=len(img_nums),
                                                              stim_maker=stim_maker)

                    for img_num, cells_to_use, xx_to_use_ctr, yy_to_use_ctr in zip(img_nums,
                                                                                   all_cells_to_use,
                                                                                   all_xx_to_use_ctr,
                                                                                   all_yy_to_use_ctr):
                        _make_stim(img_num, cells_to_use, xx_to_use_ctr, yy_to_use_ctr)

    csv_filename = root_output_dir.joinpath(csv_filename)
    make_csv(rows, csv_filename)
