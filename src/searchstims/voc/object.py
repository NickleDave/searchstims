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
