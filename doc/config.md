# Structure of config.ini files

Below is an example `config.ini` file, taken from [doc/configs](doc/configs/).
Notice each `.ini` file should have two sections. The first, called `[general]`, specifies options that 
can apply to any type of stimulus. The second, that you will name the type of visual search stimulus 
you want to generate (see valid names below), specifies options for the stimulus.

```Ini
[general]
num_target_present = 3200
num_target_absent = 3200
set_sizes = [1, 2, 4, 6, 8]
output_dir = ~/output
json_filename = filenames_by_set_size_and_target.json

[RVvGV]
rects_width_height = (10,30)
```

## `[general]` section

* `num_target_present`, `num_target_absent` : int  
  total number of samples (AKA stimuli) to generate where the target is present / absent
* `set_sizes` : list  
  of different set sizes. The exact number of samples you get for each set size will be the total 
number divided by the length of this list. E.g., If `num_target_present = 25`, and `num_target_absent = 25`, and
`set_sizes = [1, 2, 4, 6, 8]` (which has a length of five), there will be 10 samples (5 with target present, 
5 with it absent) for each set size.
* `output_dir` : str  
  path to where you want to save the generated
* `json_filename` : str
  name of file to save as .json which contains all the stimuli image filenames, that can 
then be loaded as a Python dictionary with the keys `present` and `absent`. 

## `[stimulus]` section
Currently valid stimulus types are `RGvGV` and `2_v_5`. Options common to both are defined here. 
Stimulus-specific options are defined in the sections below that show defaults values for each stimulus.

* `rects_width_height` : tuple  
    two elements, width and height of rectangle. Width first because Pygame expects this order.
* `image_size` : tuple  
    two elements, height and width of output image
* `border_size` : tuple  
    two elements, height and width of border within image. No items will be placed beyond this
    border. This option is useful when testing for edge effects.
* `grid_size` : tuple  
    two elements, height and width of grid in which items will be placed, e.g. (5, 5). The height and 
    width of each cell in the grid will be `(image_size[0] / grid_size[0], image_size[1] / grid_size[1])` 
* `jitter` : int
* `target_color` : str
   color of target. Colors are defined as RGB in a Python dictionary. You specify a color by its name listed 
   below as the key of the dictionary:

       colors_dict = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'red255green51': (255, 51, 0),
        'green255red51': (51, 255, 0),
        'red255green102': (255, 102, 0),
        'green255red102': (102, 255, 0),
        'red255green153': (255, 153, 0),
        'green255red153': (153, 255, 0),
        'red255green204': (255, 204, 0),
        'green255red204': (204, 255, 0),
    }

    Notice the colors defined in terms of how they move from either red or green towards yellow (because of how 
RGB color space works); this makes it possible to vary the discriminability of the target and distractor along a 
single feature dimension (color). Using this, one can fit a psychometric curve to the classifications of a neural 
network and estimate its accuracy level for a known discriminability of targets from distractors. **Please note also
that these latter colors only work for the `rectangle` stimulus; for the `number` stimulus valid colors are limited
to: `{'white', 'red', 'green'}`.

* `distractor_color` : str
   color of distractors. Specified in the same way as `target_color`.

### `[RGvGV]`
Colored rectangles, a typical stimulus that allows for "efficient" search.
The defaults are as follows:
```ini
[rectangle]
rects_width_height = (10, 30)
image_size = (227, 227)
border_size = None
grid_size = (5, 5)
jitter = 5
target_color = red
distractor_color = green
```

### `[2_v_5]`
Digital 5s and 2s, a stimulus that results in "inefficient" search.
The defaults are as follows:
```ini
[number]
rects_width_height = (30, 30)
image_size = (227, 227)
border_size = None
grid_size = (5, 5)
jitter = 5
target_color = white
distractor_color = white
target_number = 2
distractor_number = 5
```
