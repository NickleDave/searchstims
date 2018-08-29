import os

import pygame
from pygame.locals import *
import numpy as np

pygame.init()

# set up colors
colors_dict = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
}

png_path = os.path.join(os.path.dirname(__file__),
                        'png')

numbers_dict = {
    (2, 'red'): 'two_red.png',
    (2, 'green'): 'two_green.png',
    (2, 'white'): 'two_white.png',
    (5, 'red'): 'five_red.png',
    (5, 'green'): 'five_green.png',
    (5, 'white'): 'five_white.png',
}


def make_rectangle_stim(set_size=8,
                        num_target=1,
                        target_color='red',
                        distractor_color='green',
                        grid_size=(5, 5),
                        window_size=(227, 227),
                        rects_width_height=(10, 30),
                        jitter=5):
    """make visual search stimuli with rectangles"""
    if type(set_size) != int:
        raise TypeError('set size must be an integer')

    if not set_size > 0:
        raise ValueError('set size must be greater than zero')

    if type(num_target) != int:
        raise TypeError('number of targets must be an integer')

    if not num_target >= 0:
        raise ValueError('number of targets must be greater than or equal to zero')

    if num_target > set_size:
        raise ValueError('number of targets cannot be greater than set size')

    if not all([type(grid_size_el) == int for grid_size_el in grid_size]):
        raise ValueError('values for grid size must be positive integers')

    if not all([grid_size_el > 0 for grid_size_el in grid_size]):
        raise ValueError('values for grid size must be positive integers')

    total_grid_elements = grid_size[0] * grid_size[1]
    if set_size > total_grid_elements:
        raise ValueError('set size {} cannot be greater than number of '
                         'elements in grid, {}'
                         .format(set_size, total_grid_elements))

    if type(jitter) != int:
        raise TypeError('value for jitter must be an integer')

    # make grid, randomly select which cells in grid to use
    grid_x = np.arange(1, grid_size[0] + 1)
    grid_y = np.arange(1, grid_size[1] + 1)
    xx, yy = np.meshgrid(grid_x, grid_y)
    xx = xx.ravel()
    yy = yy.ravel()
    num_cells = grid_size[0] * grid_size[1]
    cells_to_use = sorted(np.random.choice(np.arange(num_cells),
                                           size=set_size,
                                           replace=False))
    xx_to_use = xx[cells_to_use]
    yy_to_use = yy[cells_to_use]

    # find centers of cells we're going to use
    cell_width = round(window_size[0] / grid_size[0])
    cell_x_center = round((window_size[0] / grid_size[0]) / 2)
    xx_to_use_ctr = (xx_to_use * cell_width) - cell_x_center
    cell_height = round(window_size[1] / grid_size[1])
    cell_y_center = round((window_size[1] / grid_size[1]) / 2)
    yy_to_use_ctr = (yy_to_use * cell_height) - cell_y_center

    # add jitter to those points
    jitter_high = jitter // 2
    jitter_low = -jitter_high
    if jitter % 2 == 0:  # if even
        # have to account for zero at center of jitter range
        # (otherwise range would be jitter + 1)
        # (Not a problem when doing floor division on odd #s)
        coin_flip = np.random.choice([0, 1])
        if coin_flip == 0:
            jitter_low += 1
        elif coin_flip == 1:
            jitter_high -= 1
    jitter_range = np.arange(jitter_low, jitter_high + 1)

    x_jitter = np.random.choice(jitter_range, size=xx_to_use.size)
    xx_to_use_ctr += x_jitter
    y_jitter = np.random.choice(jitter_range, size=yy_to_use.size)
    yy_to_use_ctr += y_jitter

    # set up window
    DISPLAYSURF = pygame.display.set_mode(window_size, 0, 32)

    # draw on surface object
    DISPLAYSURF.fill(colors_dict['black'])
    target_inds = np.random.choice(np.arange(set_size),
                                   size=num_target).tolist()
    rects = []
    for item in range(set_size):
        rect_tuple = (0, 0) + rects_width_height
        rect_to_draw = Rect(rect_tuple)
        rect_to_draw.center = (xx_to_use_ctr[item], yy_to_use_ctr[item])
        if item in target_inds:
            curr_rect = pygame.draw.rect(DISPLAYSURF, colors_dict[target_color],
                                         rect_to_draw)
        else:
            curr_rect = pygame.draw.rect(DISPLAYSURF, colors_dict[distractor_color],
                                         rect_to_draw)
        rects.append(curr_rect)

    pygame.display.update()
    return DISPLAYSURF


def make_number_stim(set_size=8,
                     num_target=1,
                     target_number=2,
                     distractor_number=5,
                     target_color='white',
                     distractor_color='white',
                     grid_size=(5, 5),
                     window_size=(227, 227),
                     rects_width_height=(30, 30),
                     jitter=5):
    """make visual search stimuli with numbers"""
    if type(set_size) != int:
        raise TypeError('set size must be an integer')

    if not set_size > 0:
        raise ValueError('set size must be greater than zero')

    if type(num_target) != int:
        raise TypeError('number of targets must be an integer')

    if not num_target >= 0:
        raise ValueError('number of targets must be greater than or equal to zero')

    if num_target > set_size:
        raise ValueError('number of targets cannot be greater than set size')

    if not all([type(grid_size_el) == int for grid_size_el in grid_size]):
        raise ValueError('values for grid size must be positive integers')

    if not all([grid_size_el > 0 for grid_size_el in grid_size]):
        raise ValueError('values for grid size must be positive integers')

    total_grid_elements = grid_size[0] * grid_size[1]
    if set_size > total_grid_elements:
        raise ValueError('set size {} cannot be greater than number of '
                         'elements in grid, {}'
                         .format(set_size, total_grid_elements))

    if type(jitter) != int:
        raise TypeError('value for jitter must be an integer')

    # make grid, randomly select which cells in grid to use
    grid_x = np.arange(1, grid_size[0] + 1)
    grid_y = np.arange(1, grid_size[1] + 1)
    xx, yy = np.meshgrid(grid_x, grid_y)
    xx = xx.ravel()
    yy = yy.ravel()
    num_cells = grid_size[0] * grid_size[1]
    cells_to_use = sorted(np.random.choice(np.arange(num_cells),
                                           size=set_size,
                                           replace=False))
    xx_to_use = xx[cells_to_use]
    yy_to_use = yy[cells_to_use]

    # find centers of cells we're going to use
    cell_width = round(window_size[0] / grid_size[0])
    cell_x_center = round((window_size[0] / grid_size[0]) / 2)
    xx_to_use_ctr = (xx_to_use * cell_width) - cell_x_center
    cell_height = round(window_size[1] / grid_size[1])
    cell_y_center = round((window_size[1] / grid_size[1]) / 2)
    yy_to_use_ctr = (yy_to_use * cell_height) - cell_y_center

    # add jitter to those points
    jitter_high = jitter // 2
    jitter_low = -jitter_high
    if jitter % 2 == 0:  # if even
        # have to account for zero at center of jitter range
        # (otherwise range would be jitter + 1)
        # (Not a problem when doing floor division on odd #s)
        coin_flip = np.random.choice([0, 1])
        if coin_flip == 0:
            jitter_low += 1
        elif coin_flip == 1:
            jitter_high -= 1
    jitter_range = np.arange(jitter_low, jitter_high + 1)

    x_jitter = np.random.choice(jitter_range, size=xx_to_use.size)
    xx_to_use_ctr += x_jitter
    y_jitter = np.random.choice(jitter_range, size=yy_to_use.size)
    yy_to_use_ctr += y_jitter

    # set up window
    DISPLAYSURF = pygame.display.set_mode(window_size, 0, 32)

    # draw on surface object
    DISPLAYSURF.fill(colors_dict['black'])
    target_inds = np.random.choice(np.arange(set_size),
                                   size=num_target).tolist()

    target_png = os.path.join(png_path,
                              numbers_dict[(target_number,target_color)])
    target = pygame.image.load(target_png)
    distractor_png = os.path.join(png_path,
                                  numbers_dict[(distractor_number,distractor_color)])
    distractor = pygame.image.load(distractor_png)

    rects = []
    for item in range(set_size):
        rect_tuple = (0, 0) + rects_width_height
        rect_to_draw = Rect(rect_tuple)
        rect_to_draw.center = (xx_to_use_ctr[item],
                               yy_to_use_ctr[item])
        if item in target_inds:
            curr_rect = DISPLAYSURF.blit(target, rect_to_draw)
        else:
            curr_rect = DISPLAYSURF.blit(distractor, rect_to_draw)
        rects.append(curr_rect)

    pygame.display.update()
    return DISPLAYSURF


if __name__ == '__main__':
    make_rectangle_stim()
