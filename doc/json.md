# `.json` output file

In addition to saving visual search stimuli in the output folder, `searchstims` 
saves information about stimuli in a `.json` output file. 

This `.json` file is provided to make it easier to work with the visual search 
image files, and analyze results obtained with them. 

For example, if you need to write a function that splits the stimuli into 
training and test sets) you can load the filenames like so:
```Python
>>> import json

>>> with open(json_filename) as searchstims_json:
>>>    searchstims_dict = json.load(searchstims_json)
>>> target_present_filenames = [stim_dict['filename']
...                             for stim_dict in stim_dict_list
...                             for is_present, stim_dict_list in present_absent_dict.items()
...                             for set_size, present_absent_dict in searchstims_dict.items()]
```

This file has a slightly complicated structure, described here. It is a 
serialized Python dictionary of dictionaries with the following key, field pairs:

    {set size: {
        'present': [
            {'filename': str,
             'grid_as_char': list,
             'target_indices': list,
             'distractor_indices': list,
             },
            {'filename': str,
             'grid_as_char': list,
             'target_indices': list,
             'distractor_indices': list,
             },
            ...             
            ],
        'absent': [
            {'filename': str,
             'grid_as_char': list,
             'target_indices': list,
             'distractor_indices': list,
             },
             ...
            ]
        },
     set size 2: {
        ...
    }

Keys at the top level are set size, the total number of targets and distractors, e.g.,
{1, 2, ..., 8}. Each set size key has as its value another dictionary,
whose keys are 'present' and 'absent', referring to the visual search target.
Each 'present' and 'absent' key has as its value a list of Python dictionaries;
each dictionary in the list has info about the actual visual search stimulus image
that it corresponds to:
    filename: str
        filename of a single visual search stimulus image. Specified relative to the root 
        of `output_dir` that was named in config.ini file used to generate the image. This 
        means you will need to `join` the `output_dir` with `filename` to load the image in your 
        own scripts.
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
