from pathlib import Path

import pygame
from pygame.rect import Rect

from .abstract_stim_maker import AbstractStimMaker
from .abstract_stim_maker import colors_dict
from ..voc import VOCObject

THIS_FILE_DIR = Path(__file__).parent


class Two_v_Five_StimMaker(AbstractStimMaker):
    """Make visual search stimuli where the target is a digital 2
    and the distractors are digital 5s."""
    forcedsquare_path = str(THIS_FILE_DIR.joinpath('..', 'ttf', 'forced_square.ttf'))

    def __init__(self,
                 target_number=2,
                 distractor_number=5,
                 **kwargs):
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
        super().__init__(**kwargs)
        self.target_number = str(target_number)
        self.distractor_number = str(distractor_number)

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

        voc_objects = []
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
                name = 't'
            else:
                is_target = False
                color = self.distractor_color
                distractor_indices.append(center)
                if self.grid_size:
                    grid_as_char[cells_to_use[item]] = 'd'
                name = 'd'

            if type(color) == str:
                color = colors_dict[color]

            font_obj = pygame.font.Font(self.forcedsquare_path, 64)
            if is_target:
                text_surface_obj = font_obj.render(self.target_number,
                                                   True, color)
            else:
                text_surface_obj = font_obj.render(self.distractor_number,
                                                   True, color)
            text_surface_obj = pygame.transform.scale(text_surface_obj,
                                                      (self.item_bbox_size[1],
                                                       self.item_bbox_size[0]))

            self.draw_item(display_surface=display_surface,
                           item_bbox=item_bbox,
                           to_blit=text_surface_obj)

            voc_objects.append(
                VOCObject(name=name,
                          xmin=item_bbox.left,
                          xmax=item_bbox.right,
                          ymin=item_bbox.bottom,
                          ymax=item_bbox.top)
            )

        return grid_as_char, target_indices, distractor_indices, voc_objects
