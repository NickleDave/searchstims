import csv
import json
from pathlib import Path
import re
from typing import NamedTuple


class SearchStimulus(NamedTuple):
    """class that represents a visual search stimulus"""
    stimulus: str
    set_size: int
    target_condition: str
    img_num: int
    root_output_dir: str
    img_file: str
    meta_file: str

    @classmethod
    def cast_row(cls, row):
        """Convert string values in given dictionary
        to corresponding SearchStimulus field type.
        """
        return {field: cls._field_types[field](value)
                for field, value in row.items()}


FIELDNAMES = list(SearchStimulus._fields)


def make_csv(rows, csv_filename):
    """utility function to make csv

    Parameters
    ----------
    rows : list
        values that will go into csv, with each element
        corresponding to a field defined by the FIELDNAMES
        constant declared in this module (searchstims.utils.FIELDNAMES).
    csv_filename : str
        name of csv file that will be created

    Notes
    -----
    Each row in a .csv file corresponds to an image generated by searchstims.
    Fields in csv files are:
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
    """
    with open(csv_filename, 'w') as f:
        writer = csv.DictWriter(f, FIELDNAMES)
        writer.writeheader()
        rowdicts = [
            dict(zip(FIELDNAMES, row))
            for row in rows
        ]
        writer.writerows(rowdicts)


def json_to_csv(json_filename, root_output_dir):
    """convert .json file output by earlier versions to a csv.
    Also creates individual .meta.json files for each individual .png file.

    Parameters
    ----------
    json_filename : str
        name of .json file to convert to .csv file
    root_output_dir : str
        absolute path to directory that is root of directories + images
        created by searchstims

    Notes
    -----
    The format of the .json files is described here for future reference
    (and so the programmer can figure out how to go from complicated nested
     dictionaries in .json to a flat "long-form" .csv):

    The .json file is a serialized Python dictionary of dictionaries
    with the following key, field pairs:

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
    with open(json_filename) as fp:
        metadict = json.load(fp)

    root_output_dir = Path(root_output_dir)
    if not root_output_dir.is_dir():
        raise NotADirectoryError(
            "value for `root_output_dir` not recognized as a directory: "
            f"{root_output_dir}"
        )

    root_output_dir = root_output_dir.absolute()

    rows = []
    for stimulus, stim_dict in metadict.items():
        for set_size, set_size_dict in stim_dict.items():
            for target_condition, list_meta_dict in set_size_dict.items():
                for meta_dict in list_meta_dict:
                    img_file = meta_dict['filename']
                    nums = re.findall('\d+', img_file)
                    img_num = nums[-1]
                    meta_file = img_file.replace('.png', '.meta.json')
                    row = [stimulus,
                           set_size,
                           target_condition,
                           img_num,
                           root_output_dir,
                           img_file,
                           meta_file]
                    rows.append(row)

                    # make .meta.json file too
                    meta_dict['img_file'] = meta_dict.pop('filename')
                    meta_file = Path(root_output_dir).joinpath(meta_file)
                    with open(meta_file, 'w') as fp:
                        json.dump(meta_dict, fp)

    # get just name, in case 'csv' appears somewhere in path like a parent directory
    csv_name = Path(json_filename).name
    csv_name = csv_name.replace('json', 'csv')
    # now assemble path to csv file using json_filename parent plus csv_name
    csv_filename = str(
        Path(json_filename).parent.joinpath(csv_name)
    )
    make_csv(rows, csv_filename)
