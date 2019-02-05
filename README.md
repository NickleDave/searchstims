# searchstims

Python package to make stimuli like those used in classic visual search experiments  
https://en.wikipedia.org/wiki/Visual_search  
... but with the exact size to feed them to your favorite neural network.

![efficient_search](doc/redvert_v_greenvert_set_size_4_target_present_55.png)
![inefficient_search](doc/two_v_five_set_size_6_target_present_78.png)

For a recent review of factors influencing visual search, please see:  
http://search.bwh.harvard.edu/new/pubs/FiveFactors_Wolfe-Horowitz_2017.pdf

## Installation
`pip install searchstims`

If you want to download and install locally into an environment with Anaconda:
`/home/you/Documents $ conda create -n searchstims-env python=3.6 numpy pygame`  
`/home/you/Documents $ source activate searchstims-env`  
`(searchstims-env) /home/you/Documents $ git clone`  
`(searchstim) /home/you/Documents $ cd searchstims`  
`(searchstim) /home/you/Documents/searchstims $ pip install -e .`  

## Usage
The `searchstims` package installs itself so that you can run it from the
command line. You will use a config.ini file to specify what you want the
package to generate. Below is how you would configure, 
taken from the example [config.ini](doc/configs/basic_config.ini) file.

```Ini
[general]
num_target_present = 25
num_target_absent = 25
set_sizes = [1, 2, 4, 6, 8]
output_dir = ~/output
json_filename = filenames_by_set_size_and_target.json
stimulus = rectangle
```

* `num_target_present`, `num_target_absent` : total number of samples (AKA stimuli) to generate where the target is present / absent
* `set_sizes` : list of different set sizes. The exact number of samples you get for each set size will be the total 
number divided by the length of this list. E.g., If `num_target_present = 25`, and `num_target_absent = 25`, and
`set_sizes = [1, 2, 4, 6, 8]` (which has a length of five), there will be 10 samples (5 with target present, 
5 with it absent) for each set size.
* `output_dir` : path to where you want to save the generated
* `json_filename` : name of file to save as .json which contains all the stimuli image filenames, that can 
then be loaded as a Python dictionary with the keys `present` and `absent`. 
* `stimulus` : either `rectangle` or `number` (examples shown above)

Running the example script will create a folder `~/output` with feature
search stimuli.  
`/home/you/Documents $ searchstims config.ini`

## `.json` output file
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
