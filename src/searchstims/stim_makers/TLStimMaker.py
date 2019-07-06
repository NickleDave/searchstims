from pathlib import Path
import random

import pygame
from pygame.rect import Rect

from .abstract_stim_maker import AbstractStimMaker
from .abstract_stim_maker import colors_dict

THIS_FILE_DIR = Path(__file__).parent


class TLStimMaker(AbstractStimMaker):

    forcedsquare_path = str(THIS_FILE_DIR.joinpath('..', 'ttf', 'forced_square.ttf'))

    """Make visual search stimuli with T and L shapes, where target T is rotated 90 degrees.
    Distractors can be same or different colors."""
    def __init__(self,
                 target_T_color=(255, 255, 51),
                 distractor_T_color=(100, 149, 237),
                 distractor_L_color=(255, 255, 51),
                 target_rotation=90,
                 distractor_rotation=180,
                 **kwargs):
        if type(target_rotation) != int or not(0 < target_rotation < 360):
            raise ValueError('target_rotation must be an integer between 1 and 359')

        if type(distractor_rotation) != int or not(0 < distractor_rotation < 360):
            raise ValueError('target_rotation must be an integer between 1 and 359')

        if target_rotation == distractor_rotation:
            raise ValueError('target rotation can not be equal to distractor rotation (because then target '
                             'is indistinguishable from distractor)')

        super().__init__(target_color=target_T_color,
                         distractor_color=distractor_T_color,
                         **kwargs)

        self.target_T_color = target_T_color
        self.distractor_T_color = distractor_T_color
        self.distractor_L_color = distractor_L_color
        self.target_rotation = target_rotation
        self.distractor_rotation = distractor_rotation

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

        # divide distractors up into T and L
        set_size = len(xx_to_use_ctr)
        num_distractors = set_size - len(target_inds)
        num_distractor_L = set_size // 2
        if len(target_inds) == 0:
            num_distractor_T = set_size // 2 - len(target_inds)
        else:
            num_distractor_T = set_size // 2

        if num_distractors % 2 == 1:  # e.g., if odd set size and target absent
            diff = num_distractors - (num_distractor_L + num_distractor_T)
            for _ in range(diff):
                if random.uniform(0, 1) > 0.5:
                    num_distractor_L += 1
                else:
                    num_distractor_T += 1

        distractor_letters = list('T' * num_distractor_T + 'L' * num_distractor_L)
        random.shuffle(distractor_letters)

        for item, (center_x, center_y) in enumerate(zip(xx_to_use_ctr, yy_to_use_ctr)):
            # notice we are now using PyGame order of sizes, (width, height)
            item_bbox_tuple = (0, 0) + (self.item_bbox_size[1], self.item_bbox_size[0])
            item_bbox = Rect(item_bbox_tuple)
            center = (int(center_x), int(center_y))
            item_bbox.center = center

            if item in target_inds:
                is_target = True
                color = self.target_T_color
                target_indices.append(center)
                if self.grid_size:
                    grid_as_char[cells_to_use[item]] = 't'
            else:
                is_target = False
                distractor_letter = distractor_letters.pop()
                if distractor_letter == 'T':
                    color = self.distractor_T_color
                elif distractor_letter == 'L':
                    color = self.distractor_L_color
                distractor_indices.append(center)
                if self.grid_size:
                    grid_as_char[cells_to_use[item]] = distractor_letter

            if type(color) == str:
                color = colors_dict[color]

            font_obj = pygame.font.Font(self.forcedsquare_path, 64)
            if is_target:
                text_surface_obj = font_obj.render('T', True, color)
            else:
                text_surface_obj = font_obj.render(distractor_letter, True, color)
            text_surface_obj = pygame.transform.scale(text_surface_obj,
                                                      (self.item_bbox_size[1], self.item_bbox_size[0]))
            if is_target:
                # rotate AFTER scaling (so same aspect ratio as un-rotated T)
                text_surface_obj = pygame.transform.rotate(text_surface_obj, self.target_rotation)
            else:
                if self.distractor_rotation > 0:
                    if random.uniform(0, 1) > 0.5:
                        text_surface_obj = pygame.transform.rotate(text_surface_obj, self.distractor_rotation)

            self.draw_item(display_surface=display_surface,
                           item_bbox=item_bbox,
                           to_blit=text_surface_obj)

        return grid_as_char, target_indices, distractor_indices

    def draw_item(self, display_surface, item_bbox, to_blit):
        """Returns target or distractor"""
        display_surface.blit(to_blit, item_bbox)
