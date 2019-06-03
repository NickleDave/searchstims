import os

import pygame
from pygame.rect import Rect

from searchstims.stim_makers import AbstractStimMaker


class Two_v_Five_StimMaker(AbstractStimMaker):
    """Make visual search stimuli where the target is a digital 2
    and the distractors are digital 5s."""
    png_path = os.path.join(os.path.dirname(__file__), '..', 'png')

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

    def draw_item(self, display_surface, item_bbox, to_blit):
        """Returns target or distractor"""
        display_surface.blit(to_blit, item_bbox)

    def _make_stim(self,
                   xx_to_use_ctr,
                   yy_to_use_ctr,
                   target_inds,
                   cells_to_use,
                   display_surface):
        """helper function used by make_stim
        that sub-classes can override if they need to do something more
        complicated when making the visual search stimulus"""
        target_indices = []
        distractor_indices = []
        if self.grid_size:
            grid_as_char = [''] * self.num_cells
        else:
            grid_as_char = None

        for item, (center_x, center_y) in enumerate(zip(xx_to_use_ctr, yy_to_use_ctr)):
            # notice we are now using PyGame order of sizes, (width, height)
            item_bbox_tuple = (0, 0) + (self.item_bbox_size[1], self.item_bbox_size[0])
            item_bbox = Rect(item_bbox_tuple)
            center = (int(center_x), int(center_y))
            item_bbox.center = center
            if item in target_inds:
                to_blit = self.target
                target_indices.append(center)
                if self.grid_size:
                    grid_as_char[cells_to_use[item]] = 't'
            else:
                to_blit = self.distractor
                distractor_indices.append(center)
                if self.grid_size:
                    grid_as_char[cells_to_use[item]] = 'd'

            self.draw_item(display_surface, item_bbox, to_blit)

        return grid_as_char, target_indices, distractor_indices
