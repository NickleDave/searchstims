# searchstims

Python package to make stimuli like those used in classic visual search experiments.  
https://en.wikipedia.org/wiki/Visual_search

![efficient_search](redvert_v_greenvert_set_size_4_target_present_55.png)
![inefficient_search](two_v_five_set_size_6_target_present_78.png)

## Installation
`pip install searchstims`

If you want to download locally and put install an environment with Anaconda:
`/home/you/Documents $ conda create -n searchstim python=3.6`
`/home/you/Documents $ source activate searchstim`
`(searchstim) /home/you/Documents $ git clone`
`(searchstim) /home/you/Documents $ cd searchstims`
`(searchstim) /home/you/Documents/searchstims $ pip install -e .`

## Usage
The `searchstims` package installs itself so that you can run it from the
command line. You will use a config.ini file to specify what you want the
package to generate. See the example [config.ini](./config.ini) for details.
Running the example script will create a folder `~/output` with feature
search stimuli.
`/home/you/Documents $ searchstims -c config.ini`