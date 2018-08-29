# searchstims

Python package to make stimuli like those used in classic visual search experiments.  
https://en.wikipedia.org/wiki/Visual_search

![efficient_search](redvert_v_greenvert_set_size_4_target_present_55.png)
![inefficient_search](two_v_five_set_size_6_target_present_78.png)

## Installation
Using Anaconda:  
`$ conda create -n searchstim python=3.6`  
`$ source activate searchstim`  
`(searchstim) $ pip install pygame`  
`(searchstim) $ conda install numpy`  

## Usage
Running the example script will create a folder `./output` with feature
search stimuli.  
`(searchstim) $ cd ./searchstims`  
`(searchstim) $ python script.py -c config.ini`  