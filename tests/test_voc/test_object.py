import pygame
import pytest

import searchstims.voc.object


@pytest.mark.parametrize(
    'left, top, width, height',
    [
        (0, 0, 30, 50),
        (0, 0, 227, 227),
    ]
)
def test_from_rect(left,
                   top,
                   width,
                   height):
    a_rect = pygame.Rect(left, top, width, height)

    an_object = searchstims.voc.object.VOCObject.from_rect(rect=a_rect, voc_name='dummy')
    assert an_object.xmin == left
    assert an_object.xmax == left + width
    assert an_object.ymin == top
    assert an_object.ymax == top + height
    assert an_object.xmax > an_object.xmin
    assert an_object.ymax > an_object.ymin
