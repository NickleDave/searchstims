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
command line. You will use a config.ini file to specify the visual search stimuli 
you want the package to generate.  

`/home/you/Documents $ searchstims config.ini`  

Running the example script will create a folder `~/output` with visual search stimuli. 
For more detail on the structure of `config.ini` files used with this package, see 
[./doc/config.md](./doc/config/md).

## `.json` output file
In addition to saving visual search stimuli in the output folder, `searchstims` 
saves information about stimuli in a `.json` output file.  This `.json` file is 
provided to make it easier to work with the visual search image files, 
and analyze results obtained with them. For more detail, see [./doc/json.md](./doc/json.md)

## Acknowledgments
- Research funded by the Lifelong Learning Machines program, 
DARPA/Microsystems Technology Office, 
DARPA cooperative agreement HR0011-18-2-0019
