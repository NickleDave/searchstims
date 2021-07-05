from typing import NamedTuple


class VOCObject(NamedTuple):
    """an <object> that appears in the Pascal VOC XML annotation

    used to save Pascal VOC annotations of search displays
    """
    name: str
    xmin: int
    xmax: int
    ymin: int
    ymax: int

    @classmethod
    def from_rect(cls, rect, voc_name):
        """create a ``VOCObject`` instance
        from a ``pygame.Rect``. """
        return cls(name=voc_name,
                   xmin=rect.left,
                   xmax=rect.right,
                   ymin=rect.top,
                   ymax=rect.bottom)
