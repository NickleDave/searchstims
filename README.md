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
taken from the example [config.ini](doc/config.ini) file.

```Ini
[config]
num_target_present = 3200
num_target_absent = 3200
set_sizes = [1, 2, 4, 6, 8]
output_dir = ~/output
json_filename = filenames_by_set_size_and_target.json
stimulus = number
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
`/home/you/Documents $ searchstims -c config.ini`

Then if you need to work with all the files (e.g. make a function that splits them into 
training and test sets) you can load the filenames with the `json_filename` like so:
```Python
>>> import json

>>> with open(json_filename) as searchstims_json:
>>>    searchstims_dict = json.load(searchstims_json)
```
