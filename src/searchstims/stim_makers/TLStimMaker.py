from pathlib import Path

import pygame
from pygame.rect import Rect

from .abstract_stim_maker import AbstractStimMaker
from .abstract_stim_maker import colors_dict

THIS_FILE_DIR = Path(__file__).parent


class TLStimMaker(AbstractStimMaker):

    forcedsquare_path = str(THIS_FILE_DIR.joinpath('..', 'ttf', 'forced_square.ttf'))

    """Make visual search stimuli with T shapes, where target is rotated 90 degrees."""
    def __init__(self,
                 target_color='white',
                 distractor_color='white',
                 target_rotation=90,
                 **kwargs):
        if type(target_rotation) != int or not(0 < target_rotation < 360):
            raise ValueError('target_rotation must be an integer between 1 and 359')

        super().__init__(target_color=target_color,
                         distractor_color=distractor_color,
                         **kwargs)

        self.target_rotation = target_rotation

    def _make_stim(self,
                   xx_to_use_ctr,
                   yy_to_use_ctr,
                   target_inds,
                   cells_to_use,
                   display_surface):
        """helper function used by make_stim that sub-classes can override if they need to do something more
        complicated when making the visual search stimulus

        uses xx_to_use_ctr and yy_to_use_ctr to create item_bbox Rects for each item in the visual search stimulus.
        If the item's index is in the list of target_inds then it is a target and the target color is used.

        Each item is drawn while looping through (xx_to_use_ctr, yy_to_use_ctr) by calling self.draw_item
        """
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
                is_target = True
                color = self.target_color
                target_indices.append(center)
                if self.grid_size:
                    grid_as_char[cells_to_use[item]] = 't'
            else:
                is_target = False
                color = self.distractor_color
                distractor_indices.append(center)
                if self.grid_size:
                    grid_as_char[cells_to_use[item]] = 'd'

            if type(color) == str:
                color = colors_dict[color]

            font_obj = pygame.font.Font(self.forcedsquare_path, 64)
            if is_target:
                text_surface_obj = font_obj.render('T', True, color)
            else:
                text_surface_obj = font_obj.render('L', True, color)
            text_surface_obj = pygame.transform.scale(text_surface_obj,
                                                      (self.item_bbox_size[1], self.item_bbox_size[0]))
            if is_target:
                # rotate AFTER scaling (so same aspect ratio as un-rotated T)
                text_surface_obj = pygame.transform.rotate(text_surface_obj, self.target_rotation)

            self.draw_item(display_surface=display_surface,
                           item_bbox=item_bbox,
                           to_blit=text_surface_obj)

        return grid_as_char, target_indices, distractor_indices

    def draw_item(self, display_surface, item_bbox, to_blit):
        """Returns target or distractor"""
        display_surface.blit(to_blit, item_bbox)
