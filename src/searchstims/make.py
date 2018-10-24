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


class AbstractStimMaker:
    """parent class for all StimMaker classes"""
    def __init__(self,
                 set_size=8,
                 num_target=1,
                 target_color='red',
                 distractor_color='green',
                 grid_size=(5, 5),
                 window_size=(227, 227),
                 rects_width_height=(10, 30),
                 jitter=5):
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

        self.set_size = set_size
        self.num_target = num_target
        self.target_color = target_color
        self.distractor_color = distractor_color
        self.grid_size = grid_size
        self.window_size = window_size
        self.rects_width_height = rects_width_height
        self.jitter = jitter

    def _return_rect_for_stim(self, display_surface, rect_to_draw, is_target):
        """this function must return a pygame.rect object
        which the StimMaker.make_stim method will `blit` on
        the stimulus."""
        raise NotImplementedError

    def make_stim(self):
        """make visual search stimuli with rectangles"""

        total_grid_elements = self.grid_size[0] * self.grid_size[1]
        if self.set_size > total_grid_elements:
            raise ValueError('set size {} cannot be greater than number of '
                             'elements in grid, {}'
                             .format(self.set_size, total_grid_elements))

        if type(self.jitter) != int:
            raise TypeError('value for jitter must be an integer')

        # make grid, randomly select which cells in grid to use
        grid_x = np.arange(1, self.grid_size[0] + 1)
        grid_y = np.arange(1, self.grid_size[1] + 1)
        xx, yy = np.meshgrid(grid_x, grid_y)
        xx = xx.ravel()
        yy = yy.ravel()
        num_cells = self.grid_size[0] * self.grid_size[1]
        cells_to_use = sorted(np.random.choice(np.arange(num_cells),
                                               size=self.set_size,
                                               replace=False))
        xx_to_use = xx[cells_to_use]
        yy_to_use = yy[cells_to_use]

        # find centers of cells we're going to use
        cell_width = round(self.window_size[0] / self.grid_size[0])
        cell_x_center = round((self.window_size[0] / self.grid_size[0]) / 2)
        xx_to_use_ctr = (xx_to_use * cell_width) - cell_x_center
        cell_height = round(self.window_size[1] / self.grid_size[1])
        cell_y_center = round((self.window_size[1] / self.grid_size[1]) / 2)
        yy_to_use_ctr = (yy_to_use * cell_height) - cell_y_center

        # add jitter to those points
        jitter_high = self.jitter // 2
        jitter_low = -jitter_high
        if self.jitter % 2 == 0:  # if even
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
        display_surface = pygame.display.set_mode(self.window_size, 0, 32)

        # draw on surface object
        display_surface.fill(colors_dict['black'])
        target_inds = np.random.choice(np.arange(self.set_size),
                                       size=self.num_target).tolist()
        rects = []
        for item in range(self.set_size):
            rect_tuple = (0, 0) + self.rects_width_height
            rect_to_draw = Rect(rect_tuple)
            rect_to_draw.center = (xx_to_use_ctr[item], yy_to_use_ctr[item])
            if item in target_inds:
                is_target = True
            else:
                is_target = False
            curr_rect = self._return_rect_for_stim(display_surface=display_surface,
                                                   rect_to_draw=rect_to_draw,
                                                   is_target=is_target)
            rects.append(curr_rect)
        pygame.display.update()
        return display_surface


class RectangleStimMaker(AbstractStimMaker):
    """make visual search stimuli with rectangles"""
    def _return_rect_for_stim(self, display_surface, rect_to_draw, is_target):
        if is_target:
            color = self.target_color
        else:
            color = self.distractor_color
        rect = pygame.draw.rect(display_surface, colors_dict[color], rect_to_draw)
        return rect


class NumberStimMaker(AbstractStimMaker):
    """make visual search stimuli with numbers"""
    png_path = os.path.join(os.path.dirname(__file__), 'png')

    numbers_dict = {
        (2, 'red'): 'two_red.png',
        (2, 'green'): 'two_green.png',
        (2, 'white'): 'two_white.png',
        (5, 'red'): 'five_red.png',
        (5, 'green'): 'five_green.png',
        (5, 'white'): 'five_white.png',
    }

    def __init__(self,
                 set_size=8,
                 num_target=1,
                 target_number=2,
                 distractor_number=5,
                 target_color='white',
                 distractor_color='white',
                 grid_size=(5, 5),
                 window_size=(227, 227),
                 rects_width_height=(30, 30),
                 jitter=5):
        super().__init__(set_size,
                         num_target,
                         target_color,
                         distractor_color,
                         grid_size,
                         window_size,
                         rects_width_height,
                         jitter)
        self.target_number = target_number
        self.distractor_number = distractor_number
        self.target_png = os.path.join(self.png_path,
                                       self.numbers_dict[(self.target_number,
                                                          self.target_color)])
        self.target = pygame.image.load(self.target_png)
        self.distractor_png = os.path.join(self.png_path,
                                           self.numbers_dict[(self.distractor_number,
                                                              self.distractor_color)])
        self.distractor = pygame.image.load(self.distractor_png)

    def _return_rect_for_stim(self, display_surface, rect_to_draw, is_target):
        if is_target:
            rect = display_surface.blit(self.target, rect_to_draw)
        else:
            rect = display_surface.blit(self.distractor, rect_to_draw)
        return rect
