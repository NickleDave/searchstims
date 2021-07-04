from pathlib import Path
import random

import pygame
from pygame.rect import Rect

from .abstract_stim_maker import AbstractStimMaker
from .abstract_stim_maker import colors_dict
from ..voc import VOCObject

THIS_FILE_DIR = Path(__file__).parent


class xoStimMaker(AbstractStimMaker):

    forcedsquare_path = str(THIS_FILE_DIR.joinpath('..', 'ttf', 'forced_square.ttf'))

    """Make visual search stimuli where target is 'x' and distractors are 'x's and 'o's.
    Distractors can be same or different colors.
    """
    def __init__(self,
                 target_x_color='blue',
                 distractor_x_color='red',
                 distractor_o_color='red',
                 **kwargs):
        super().__init__(target_color=target_x_color,
                         distractor_color=distractor_x_color,
                         **kwargs)

        self.target_x_color = target_x_color
        self.distractor_x_color = distractor_x_color
        self.distractor_o_color = distractor_o_color

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

        # divide distractors up into x and o
        set_size = len(xx_to_use_ctr)
        num_distractors = set_size - len(target_inds)
        num_distractor_o = set_size // 2
        if len(target_inds) == 0:
            num_distractor_x = set_size // 2 - len(target_inds)
        else:
            num_distractor_x = set_size // 2

        if num_distractors % 2 == 1:  # e.g., if odd set size and target absent
            diff = num_distractors - (num_distractor_o + num_distractor_x)
            for _ in range(diff):
                if random.uniform(0, 1) > 0.5:
                    num_distractor_o += 1
                else:
                    num_distractor_x += 1

        distractor_letters = list('x' * num_distractor_x + 'o' * num_distractor_o)
        random.shuffle(distractor_letters)

        voc_objects = []
        for item, (center_x, center_y) in enumerate(zip(xx_to_use_ctr, yy_to_use_ctr)):
            # notice we are now using PyGame order of sizes, (width, height)
            item_bbox_tuple = (0, 0) + (self.item_bbox_size[1], self.item_bbox_size[0])
            item_bbox = Rect(item_bbox_tuple)
            center = (int(center_x), int(center_y))
            item_bbox.center = center

            if item in target_inds:
                is_target = True
                color = self.target_x_color
                target_indices.append(center)
                if self.grid_size:
                    grid_as_char[cells_to_use[item]] = 't'
                voc_name = 't'
            else:
                is_target = False
                distractor_letter = distractor_letters.pop()
                if distractor_letter == 'x':
                    color = self.distractor_x_color
                    voc_name = 'dx'
                elif distractor_letter == 'o':
                    color = self.distractor_o_color
                    voc_name = 'do'
                distractor_indices.append(center)
                if self.grid_size:
                    grid_as_char[cells_to_use[item]] = distractor_letter

            if type(color) == str:
                color = colors_dict[color]

            font_obj = pygame.font.Font(self.forcedsquare_path, 64)
            if is_target:
                text_surface_obj = font_obj.render('x', True, color)
            else:
                text_surface_obj = font_obj.render(distractor_letter, True, color)
            text_surface_obj = pygame.transform.scale(text_surface_obj,
                                                      (self.item_bbox_size[1], self.item_bbox_size[0]))

            self.draw_item(display_surface=display_surface,
                           item_bbox=item_bbox,
                           to_blit=text_surface_obj)

            voc_objects.append(
                VOCObject(name=voc_name,
                          xmin=item_bbox.left,
                          xmax=item_bbox.right,
                          ymin=item_bbox.bottom,
                          ymax=item_bbox.top)
            )

        return grid_as_char, target_indices, distractor_indices, voc_objects

    def draw_item(self, display_surface, item_bbox, to_blit):
        """Returns target or distractor"""
        display_surface.blit(to_blit, item_bbox)
