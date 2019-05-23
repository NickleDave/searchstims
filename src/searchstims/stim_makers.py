import os
from collections import namedtuple

import pygame
from pygame.locals import *
import numpy as np
from scipy.spatial.distance import pdist

pygame.init()

# set up colors
colors_dict = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'red255green51': (255, 51, 0),
    'green255red51': (51, 255, 0),
    'red255green102': (255, 102, 0),
    'green255red102': (102, 255, 0),
    'red255green153': (255, 153, 0),
    'green255red153': (153, 255, 0),
    'red255green204': (255, 204, 0),
    'green255red204': (204, 255, 0),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
}

MAX_DRAWS_INNER = 1000
MAX_DRAWS_OUTER = 100


class AbstractStimMaker:
    """parent class for all StimMaker classes

    Attributes
    ----------
    target_color : str
        {'red', 'green', 'white', 'blue'}. Default is 'red'.
    distractor_color : str
        {'red', 'green', 'white', 'blue'}. Default is 'green'.
    window_size : tuple
        of length two, representing (height, width) of window in pixels.
    border_size : tuple
        of length two, representing (height, width) of border, distance
        from edge of window within which items should not be displayed.
        Default is None.
    grid_size : tuple
        of length two, representing the number of (rows, columns)
        in the grid on which target and distractors will be located.
    min_center_dist : int
        Minimum distance between center point of items. Default is None, in
        which case any distance is permitted. Only used if grid_size is None
        and items are placed randomly instead of on a grid.
    item_bbox_size : tuple
        shape of "bounding box" that contains items to be plotted,
        (height, width) in pixels. Default is (30, 30).
    jitter : int
        number of pixels to jitter each 'item' in the 'set'
        that will be plotted on the grid. Default is 5.
        Adding jitter is helpful for creating stimuli with the
        same set size but slightly different placements, e.g. for
        augmenting data to train a learning algorithm and encourage
        invariant representations.
    num_cells : int
        rows * columns in grid
    grid_size_pixels : tuple
        (width, height). Size of grid in pixels. Either equal to window size, or if
        border size is not None, equal to window size minus border size.
    yy : numpy.ndarray
       y-axis co-ordinates of cells, e.g. [0, 1, 2, 3, 4] for an y-axis with 5 cells.
    xx : numpy.ndarray
        x-axis co-ordinates of cells, e.g. [0, 1, 2, 3, 4] for an x-axis with 5 cells.
    cell_height : int
        height of a cell in grid, in pixels
    cell_y_center : int
        co-ordinate of center of y axis of a cell. Add to co-ordinate of cell corner to
        get the center point of cell within the entire window.
    cell_width : int
        width of a cell in grid, in pixels
    cell_x_center
        co-ordinate of center of x axis of a cell. Add to co-ordinate of cell corner to
        get the center point of cell within the entire window.
    """

    RectTuple = namedtuple('RectTuple', ['display_surface',
                                         'grid_as_char',
                                         'target_indices',
                                         'distractor_indices'])

    def __init__(self,
                 target_color='red',
                 distractor_color='green',
                 window_size=(227, 227),
                 border_size=None,
                 grid_size=(5, 5),
                 min_center_dist=None,
                 item_bbox_size=(30, 30),
                 jitter=5):
        """__init__ function for Stim Makers

        Parameters
        ----------
        target_color : str, tuple
            {'red', 'green', 'white', 'blue'}. Default is 'red'.
        distractor_color : str, tuple
            {'red', 'green', 'white', 'blue'}. Default is 'green'.
        window_size : tuple
            of length two, representing (height, width) of window in pixels.
        border_size : tuple
            of length two, representing (height, width) of border, distance
            from edge of window within which items should not be displayed.
            Default is None.
        grid_size : tuple
            of length two, representing the number of (rows, columns)
            in the grid on which target and distractors will be located.
        min_center_dist : int
            Minimum distance between center point of items. Default is None, in
            which case any distance is permitted. Only used if grid_size is None
            and items are placed randomly instead of on a grid.
        item_bbox_size : tuple
            shape of "bounding box" that contains items to be plotted,
            (height, width) in pixels. Default is (30, 30).
        jitter : int
            number of pixels to jitter each 'item' in the 'set'
            that will be plotted on the grid. Default is 5.
            Adding jitter is helpful for creating stimuli with the
            same set size but slightly different placements, e.g. for
            augmenting data to train a learning algorithm and encourage
            invariant representations.
        """
        if grid_size is not None:
            if not all([type(grid_size_el) == int for grid_size_el in grid_size]):
                raise ValueError('values for grid size must be positive integers')

            if not all([grid_size_el > 0 for grid_size_el in grid_size]):
                raise ValueError('values for grid size must be positive integers')

        if type(target_color) not in (str, tuple):
            raise TypeError('target_color must be a string or a three-element tuple corresponding to an RGB color')

        if type(target_color) == tuple:
            if len(target_color) != 3:
                raise ValueError(
                    f'target_color tuple must be a 3 element RGB color; number of elements was {len(target_color)}'
                )
            if not all([type(el) == int for el in target_color]):
                raise ValueError(
                    'all elements in target_color tuple should be of type int'
                )

        if type(distractor_color) not in (str, tuple):
            raise TypeError('distractor_color must be a string or a three-element tuple corresponding to an RGB color')

        if type(distractor_color) == tuple:
            if len(distractor_color) != 3:
                raise ValueError(
                    'distractor_color tuple must be a 3 element RGB color; '
                    f'number of elements was {len(distractor_color)}'
                )
            if not all([type(el) == int for el in distractor_color]):
                raise ValueError(
                    'all elements in distractor_color tuple should be of type int'
                )

        self.target_color = target_color
        self.distractor_color = distractor_color
        self.grid_size = grid_size
        self.min_center_dist = min_center_dist
        self.window_size = window_size
        self.border_size = border_size
        self.item_bbox_size = item_bbox_size
        self.jitter = jitter

        if self.grid_size:
            self.num_cells = self.grid_size[0] * self.grid_size[1]

            if self.border_size is None:
                self.grid_size_pixels = self.window_size
            else:
                self.grid_size_pixels = (self.window_size[0] - self.border_size[0],
                                         self.window_size[1] - self.border_size[1])

            # make grid, randomly select which cells in grid to use.
            grid_y = np.arange(1, self.grid_size[0] + 1)
            grid_x = np.arange(1, self.grid_size[1] + 1)
            yy, xx = np.meshgrid(grid_y, grid_x)
            self.yy = yy.ravel()
            self.xx = xx.ravel()

            # find centers of cells we're going to use
            self.cell_height = round(self.grid_size_pixels[0] / self.grid_size[0])
            self.cell_y_center = round((self.grid_size_pixels[0] / self.grid_size[0]) / 2)

            self.cell_width = round(self.grid_size_pixels[1] / self.grid_size[1])
            self.cell_x_center = round((self.grid_size_pixels[1] / self.grid_size[1]) / 2)

    def draw_item(self, display_surface, item_bbox, is_target):
        """draw item for visual search stimulus

        Parameters
        ----------
        display_surface : pygame.Surface
        item_bbox : pygame.rect
            item bounding box. The actual item is drawn
            *within* this bounding box.
        is_target : bool
            if True, item to be drawn is a target.
            if False, item to be drawn is a distractor.
            How the item is drawn (color, orientation, shape, etc.) will
            depend on whether this is True or False
        """
        raise NotImplementedError

    def make_stim(self,
                  set_size=8,
                  num_target=1,
                  cells_to_use=None,
                  xx_to_use_ctr=None,
                  yy_to_use_ctr=None
                  ):
        """make visual search stimuli

        Parameters
        ----------
        set_size : int
            Set size, equal to number of targets + distractors.
            Default is 8.
        num_target : int
            Number of targets. Default is 1.
        cells_to_use : list
            list of cells in grid to use. Length must equal set_size.
            Default is None, in which case cells are drawn randomly from
            grid defined for this stim maker. The centers of the cells of
            the grid are accessible as stim_maker.xx and stim_maker.yy
        xx_to_use_ctr : numpy.ndarray
            co-ordinates of center of item bounding boxes on x axis.
            One-dimensional vector; number of elements must equal set_size.
            Default is None. If None and cells_to_use is None, cells will
            be drawn at random and the center of those cells used.
        yy_to_use_ctr : numpy.ndarray
            co-ordinates of center of item bounding boxes on y axis.
            One-dimensional vector; number of elements must equal set_size.
            Default is None. If None and cells_to_use is None, cells will
            be drawn at random and the center of those cells used.

        Returns
        -------
        display_surface : pygame.Surface
            with visual search stimuli plotted on it
        """
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

        if cells_to_use:
            if len(cells_to_use) != set_size:
                raise ValueError(f'Number of elements in cells_to_use must equal set_size.\n'
                                 f'cells_to_use has length {len(cells_to_use)} but set_size is {set_size}.')

        if xx_to_use_ctr is not None:
            if yy_to_use_ctr is None:
                raise ValueError('must pass an argument for yy_to_use_ctr when passing xx_to_use_ctr')
            if xx_to_use_ctr.ndim != 1:
                raise ValueError('xx_to_use_ctr should be a one-dimensional vector but has shape: '
                                 f'{xx_to_use_ctr.shape}')
            if xx_to_use_ctr.shape[0] != set_size:
                raise ValueError('Number of elements in xx_to_use_ctr must equal set size.'
                                 f'xx_to_use_ctr.shape is {xx_to_use_ctr.shape} and set size is {set_size}')

        if yy_to_use_ctr is not None:
            if xx_to_use_ctr is None:
                raise ValueError('must pass an argument for xx_to_use_ctr when passing yy_to_use_ctr')
            if yy_to_use_ctr.ndim != 1:
                raise ValueError('yy_to_use_ctr should be a one-dimensional vector but has shape: '
                                 f'{yy_to_use_ctr.shape}')
            if yy_to_use_ctr.shape[0] != set_size:
                raise ValueError('Number of elements in yy_to_use_ctr must equal set size.'
                                 f'yy_to_use_ctr.shape is {yy_to_use_ctr.shape} and set size is {set_size}')

        if self.grid_size is not None:
            total_grid_elements = self.grid_size[0] * self.grid_size[1]
            if set_size > total_grid_elements:
                raise ValueError('set size {} cannot be greater than number of '
                                 'elements in grid, {}'
                                 .format(set_size, total_grid_elements))

        if type(self.jitter) != int:
            raise TypeError('value for jitter must be an integer')

        ###########################################################################
        # notice: below we always refer to y before x, because shapes are         #
        # specified in order of (height, width). So size[0] = y and size[1] = x   #
        ###########################################################################
        if cells_to_use is not None or (xx_to_use_ctr is None and yy_to_use_ctr is None):
            if self.grid_size:
                if cells_to_use is None:
                    cells_to_use = sorted(np.random.choice(np.arange(self.num_cells),
                                                           size=set_size,
                                                           replace=False))

                    yy_to_use = self.yy[cells_to_use]
                    xx_to_use = self.xx[cells_to_use]

                    # find centers of cells we're going to use
                    yy_to_use_ctr = (yy_to_use * self.cell_height) - self.cell_y_center

                    xx_to_use_ctr = (xx_to_use * self.cell_width) - self.cell_x_center

                    if self.border_size:
                        yy_to_use_ctr += round(self.border_size[0] / 2)
                        xx_to_use_ctr += round(self.border_size[1] / 2)

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

                    y_jitter = np.random.choice(jitter_range, size=yy_to_use.size)
                    yy_to_use_ctr += y_jitter
                    x_jitter = np.random.choice(jitter_range, size=xx_to_use.size)
                    xx_to_use_ctr += x_jitter

            else:  # if self.grid_size is None
                if self.border_size:
                    yy = np.arange(self.border_size[0] + (self.item_bbox_size[0] / 2),
                                   self.window_size[0] - (self.border_size[0] + (self.item_bbox_size[0] / 2) + 1),
                                   dtype=int)
                    xx = np.arange(self.border_size[1] + (self.item_bbox_size[1] / 2),
                                   self.window_size[1] - (self.border_size[1] + (self.item_bbox_size[1] / 2) + 1),
                                   dtype=int)
                else:
                    yy = np.arange(self.item_bbox_size[0] / 2,
                                   self.window_size[0] - (self.item_bbox_size[0] / 2))
                    xx = np.arange(self.item_bbox_size[1] / 2,
                                   self.window_size[1] - (self.item_bbox_size[1] / 2))

                # draw center points at random
                dists_are_good = False
                less_than_set_size = True
                draws_outer = 0
                while dists_are_good is False:
                    draws_outer += 1
                    if draws_outer > MAX_DRAWS_OUTER:
                        raise ValueError('could not find suitable set of co-ordinates for set')

                    draws_inner = 0
                    coords_list = []

                    while less_than_set_size is True:
                        yy_to_use_ctr = np.random.choice(yy)
                        xx_to_use_ctr = np.random.choice(xx)
                        coord = [xx_to_use_ctr, yy_to_use_ctr]
                        draws_inner += 1
                        if draws_inner > MAX_DRAWS_INNER:
                            coords_list = []
                            draws_inner = 0

                        if len(coords_list) == 0:
                            coords_list.append(coord)

                            if set_size == 1:
                                # then we're done actually
                                less_than_set_size = False
                                dists_are_good = True
                                # make into an array of size (1,) to prevent crash when we index into them below
                                yy_to_use_ctr = np.asarray([yy_to_use_ctr])
                                xx_to_use_ctr = np.asarray([xx_to_use_ctr])
                        else:
                            coords_list_tmp = list(coords_list)
                            coords_list_tmp.append(coord)
                            coords_list_tmp = np.stack(coords_list_tmp)
                            dists = pdist(coords_list_tmp)

                            if np.any(dists < self.min_center_dist):
                                continue
                            else:
                                coords_list = coords_list_tmp.tolist()

                                if len(coords_list) < set_size:
                                    continue
                                else:
                                    coords = np.asarray(coords_list)
                                    yy_to_use_ctr = coords[:, 1]
                                    xx_to_use_ctr = coords[:, 0]
                                    dists_are_good = True
                                    less_than_set_size = False

        # set up window
        display_surface = pygame.display.set_mode((self.window_size[1], self.window_size[0]),
                                                  0,
                                                  32)

        # draw on surface object
        display_surface.fill(colors_dict['black'])
        target_inds = np.random.choice(np.arange(set_size),
                                       size=num_target).tolist()
        target_indices = []
        distractor_indices = []
        if self.grid_size:
            grid_as_char = [''] * self.num_cells
        else:
            grid_as_char = None

        for item in range(set_size):
            # notice we are now using PyGame order of sizes, (width, height)
            item_bbox_tuple = (0, 0) + (self.item_bbox_size[1], self.item_bbox_size[0])
            item_bbox = Rect(item_bbox_tuple)
            center = (int(xx_to_use_ctr[item]), int(yy_to_use_ctr[item]))
            item_bbox.center = center
            if item in target_inds:
                is_target = True
                target_indices.append(center)
                if self.grid_size:
                    grid_as_char[cells_to_use[item]] = 't'
            else:
                is_target = False
                distractor_indices.append(center)
                if self.grid_size:
                    grid_as_char[cells_to_use[item]] = 'd'
            self.draw_item(display_surface=display_surface,
                           item_bbox=item_bbox,
                           is_target=is_target)

        if self.grid_size:
            grid_as_char = np.asarray(grid_as_char).reshape(self.grid_size[0], self.grid_size[1]).tolist()

        pygame.display.update()
        return self.RectTuple(display_surface=display_surface,
                              grid_as_char=grid_as_char,
                              target_indices=target_indices,
                              distractor_indices=distractor_indices)


class RVvGVStimMaker(AbstractStimMaker):
    """Make visual search stimuli with vertical rectangles
    where target is red and distractors are green."""
    def draw_item(self, display_surface, item_bbox, is_target):
        """Draws a vertical rectangle that is 1/3 the width of the item bounding box.

        Parameters
        ----------
        display_surface : pygame.Surface
            instance of Surface on which to draw item
        item_bbox : pygame.Rect
            instance of Rect that represents 'bounding box' within which
            item should be drawn.
        is_target : bool
            if True, item to draw is target and target color should be used

        Returns
        -------
        None
        """
        if is_target:
            color = self.target_color
        else:
            color = self.distractor_color

        if type(color) == str:
            color = colors_dict[color]

        rect_to_draw = item_bbox  # yes, they point to the same object

        width = rect_to_draw.width
        width = width // 3
        rect_to_draw.width = width
        rect_to_draw.left = rect_to_draw.left + width

        pygame.draw.rect(display_surface, color, rect_to_draw)


class Two_v_Five_StimMaker(AbstractStimMaker):
    """Make visual search stimuli where the target is a digital 2
    and the distractors are digital 5s."""
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
                 target_color='white',
                 distractor_color='white',
                 grid_size=(5, 5),
                 min_center_dist=None,
                 window_size=(227, 227),
                 border_size=None,
                 item_bbox_size=(30, 30),
                 jitter=5,
                 target_number=2,
                 distractor_number=5):
        """
        Other Parameters
        ----------------
        target_number : int
            Number that is used as target.
            one of {2, 5}. Default is 2.
        distractor_number : int
            Number that is used as a distractor.
            one of {2, 5}. Default is 5.
        """
        super().__init__(target_color=target_color,
                         distractor_color=distractor_color,
                         window_size=window_size,
                         border_size=border_size,
                         grid_size=grid_size,
                         min_center_dist=min_center_dist,
                         item_bbox_size=item_bbox_size,
                         jitter=jitter)
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

    def draw_item(self, display_surface, item_bbox, is_target):
        """Returns target or distractor"""
        if is_target:
            display_surface.blit(self.target, item_bbox)
        else:
            display_surface.blit(self.distractor, item_bbox)
