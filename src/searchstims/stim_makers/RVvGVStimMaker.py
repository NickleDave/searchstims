import pygame

from .abstract_stim_maker import AbstractStimMaker


class RVvGVStimMaker(AbstractStimMaker):
    """Make visual search stimuli with vertical rectangles
    where target is red and distractors are green."""
    def draw_item(self, display_surface, item_bbox, color):
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
        rect_to_draw = item_bbox  # yes, they point to the same object

        width = rect_to_draw.width
        width = width // 3
        rect_to_draw.width = width
        rect_to_draw.left = rect_to_draw.left + width

        pygame.draw.rect(display_surface, color, rect_to_draw)
