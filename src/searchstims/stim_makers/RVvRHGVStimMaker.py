import random

import pygame
from pygame.rect import Rect

from .abstract_stim_maker import AbstractStimMaker
from .abstract_stim_maker import colors_dict


class RVvRHGVStimMaker(AbstractStimMaker):
    """Make visual search stimuli with rectangles,
    where target is red vertical rectangle. Half of distractors
    will be vertical green rectangles and the other half will
    be horizontal red rectangles. If the target is present,
    then (half - 1) of the distractors will be horizontal red
    rectangles."""

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

        num_distractors = set_size - len(target_inds)
        num_vert_rect = set_size // 2
        if len(target_inds) == 0:
            num_horz_rect = set_size // 2 - len(target_inds)
        else:
            num_horz_rect = set_size // 2

        if num_distractors % 2 == 1:  # e.g., if odd set size and target absent
            diff = num_distractors - (num_vert_rect + num_horz_rect)
            for _ in range(diff):
                if random.uniform(0, 1) > 0.5:
                    num_vert_rect += 1
                else:
                    num_horz_rect += 1

        distractor_orientation = list('V' * num_vert_rect + 'H' * num_horz_rect)
        random.shuffle(distractor_orientation)

        for item, (center_x, center_y) in enumerate(zip(xx_to_use_ctr, yy_to_use_ctr)):
            # notice we are now using PyGame order of sizes, (width, height)
            item_bbox_tuple = (0, 0) + (self.item_bbox_size[1], self.item_bbox_size[0])
            item_bbox = Rect(item_bbox_tuple)
            center = (int(center_x), int(center_y))
            item_bbox.center = center

            if item in target_inds:
                color = self.target_color
                rotate = False
                target_indices.append(center)
                if self.grid_size:
                    grid_as_char[cells_to_use[item]] = 't'
            else:
                orientation = distractor_orientation.pop()
                if orientation == 'V':
                    color = self.distractor_color
                    rotate = False
                elif orientation == 'H':
                    color = self.target_color
                    rotate = True

                distractor_indices.append(center)
                if self.grid_size:
                    grid_as_char[cells_to_use[item]] = orientation
                    # instead of 'd', so we know which distractor is which

            if type(color) == str:
                color = colors_dict[color]

            self.draw_item(display_surface=display_surface,
                           item_bbox=item_bbox,
                           color=color,
                           rotate=rotate)

        return grid_as_char, target_indices, distractor_indices

    def draw_item(self, display_surface, item_bbox, color, rotate):
        """Draws a vertical rectangle that is 1/3 the width of the item bounding box.

        Parameters
        ----------
        display_surface : pygame.Surface
            instance of Surface on which to draw item
        item_bbox : pygame.Rect
            instance of Rect that represents 'bounding box' within which
            item should be drawn.

        Returns
        -------
        None
        """
        # rect_to_draw is same object as item_bbox, but we're going to change the
        # "bounding box" into the items we will draw
        rect_to_draw = item_bbox

        if rotate:
            height = rect_to_draw.height // 3
            rect_to_draw.height = height
            rect_to_draw.bottom = rect_to_draw.bottom + height
        else:
            width = rect_to_draw.width // 3
            rect_to_draw.width = width
            rect_to_draw.left = rect_to_draw.left + width

        pygame.draw.rect(display_surface, color, rect_to_draw)
