""" classes to represent sections of config.ini file """
import attr
from attr.validators import instance_of, optional
from attr import converters

def check_len_is_two(instance, attribute, value):
    if len(value) != 2:
        raise ValueError(f"{attribute.name} tuple for {instance.name} should be two elements, got {value}")


@attr.s
class GeneralConfig:
    """represents [GENERAL] section of config.ini file

    Attributes
    ----------
    output_dir : str
        path to directory where images and .json file created by running searchstims
        should be saved
    json_filename : str
        name of .json file that will be created with information about images created
    enforce_unique : bool
        if True, ensures that each stimulus is unique by drawing without replacement all
        item locations *before* generating any of the stimuli

    The remaining attributes, if declared as options and assigned values in the [GENERAL] section
    of a config.ini file, will be used for all stimuli *unless* the same options are declared in
    a section for a specific stimulus, in which case those values override the values assigned to
    the attributes in the [GENERAL[ section (and thus the GeneralConfig instance that represents it).

    num_target_present : int
        number of visual search stimuli to generate with target present.
    num_target_absent : int
        number of visual search stimuli to generate with target absent
    set_sizes : list
        of int, "set sizes" that should be generated
    item_bbox_size : tuple
        two element tuple, (height, width). The size of the
        "bounding box" that contains items (target + distractors) in the visual search stimulus.
    image_size : tuple
        two element tuple, (height, width). This will be the size of an input
        to the neural network architecture that you're training.
    grid_size : tuple
        two element tuple, (rows, columns). Represents the "grid" that the
        visuals search stimulus is divided into, where each cell in that
        grid can contain an item (either the target or a distractor). The
        total number of cells will be rows * columns.
    border_size : tuple
        two element tuple, (height, width). The size of the border between
        the actual end of the image and the grid of cells within the image
        that will contain the items (target + distractors).
        Useful if you are worried about edge effects.
    min_center_dist : int
        minimum distance to maintain between the center of items.
        Useful if you are worried about crowding effects.
    jitter : int
        maximum value of jitter applied to center points of items.
    """
    output_dir = attr.ib(validator=instance_of(str))
    json_filename = attr.ib(validator=instance_of(str))
    num_target_present = attr.ib(converter=converters.optional(int))
    num_target_absent = attr.ib(converter=converters.optional(int))
    set_sizes = attr.ib(validator=optional(instance_of(list)))
    enforce_unique = attr.ib(validator=optional(instance_of(bool)), default=True)
    item_bbox_size = attr.ib(validator=optional([instance_of(tuple), check_len_is_two]),
                                 default=None)
    image_size = attr.ib(validator=optional([instance_of(tuple), check_len_is_two]),
                         default=None)
    grid_size = attr.ib(validator=optional([instance_of(tuple), check_len_is_two]),
                        default=None)
    border_size = attr.ib(validator=optional([instance_of(tuple), check_len_is_two]),
                          default=None)
    min_center_dist = attr.ib(validator=optional(instance_of(int)), default=None)
    jitter = attr.ib(validator=optional(instance_of(int)), default=None)


@attr.s
class RectangleConfig:
    """represent [RECTANGLE] section of config.ini file

    Attributes
    ----------
    item_bbox_size : tuple
        two element tuple, (height, width). The size of the
        "bounding box" that contains items (target + distractors) in the visual search stimulus.
    image_size : tuple
        two element tuple, (height, width). This will be the size of an input
        to the neural network architecture that you're training.
    grid_size : tuple
        two element tuple, (rows, columns). Represents the "grid" that the
        visuals search stimulus is divided into, where each cell in that
        grid can contain an item (either the target or a distractor). The
        total number of cells will be rows * columns.
    border_size : tuple
        two element tuple, (height, width). The size of the border between
        the actual end of the image and the grid of cells within the image
        that will contain the items (target + distractors).
        Optional; default is None. Useful if you are worried about edge effects.
    min_center_dist : int
        minimum distance to maintain between the center of items.
        Useful if you are worried about crowding effects.
        Optional; default is None.
    jitter : int
        maximum value of jitter applied to center points of items. Default is 5.
    rectangle_size : tuple
        two element tuple, (height, width). The size of the rectangle plotted
        inside the item bounding box. Default is (10, 30).
    target_color : str
        color of target. For RectangleConfig, default is 'red'.
    distractor_color : str
        color of target. For RectangleConfig, default is 'green'.
    """
    item_bbox_size = attr.ib(validator=optional([instance_of(tuple), check_len_is_two]),
                                 default=(30, 30))
    image_size = attr.ib(validator=optional([instance_of(tuple), check_len_is_two]),
                         default=(227, 227))
    grid_size = attr.ib(validator=optional([instance_of(tuple), check_len_is_two]),
                        default=(5,5))
    border_size = attr.ib(validator=optional([instance_of(tuple), check_len_is_two]),
                          default=None)
    min_center_dist = attr.ib(validator=optional(instance_of(int)), default=None)
    jitter = attr.ib(validator=optional(instance_of(int)), default=5)
    target_color = attr.ib(validator=instance_of(str), default='red')
    distractor_color = attr.ib(validator=instance_of(str), default='green')


def number_validator(instance, attribute, value):
    if value not in (2, 5):
        raise ValueError(f'{attribute} must be either 2 or 5, not {value}')
    if (
                (attribute == 'target_number' and value == instance.distractor_number)
            or
                (attribute == 'distractor_number' and value == instance.target_number)
    ):
            raise ValueError(f"target number should not equal distractor number but both are {value}")


@attr.s
class NumberConfig:
    """represent [NUMBER] section of config.ini file

    Attributes
    ----------
    item_bbox_size : tuple
        two element tuple, (height, width). The size of the
        "bounding box" that contains items (target + distractors) in the visual search stimulus.
        For NumberConfig this must be the size of the .png images that contain the
        number shapes, (30, 30).
    image_size : tuple
        two element tuple, (height, width). This will be the size of an input
        to the neural network architecture that you're training.
    grid_size : tuple
        two element tuple, (rows, columns). Represents the "grid" that the
        visuals search stimulus is divided into, where each cell in that
        grid can contain an item (either the target or a distractor). The
        total number of cells will be rows * columns.
    border_size : tuple
        two element tuple, (height, width). The size of the border between
        the actual end of the image and the grid of cells within the image
        that will contain the items (target + distractors).
        Optional; default is None. Useful if you are worried about edge effects.
    min_center_dist : int
        minimum distance to maintain between the center of items.
        Useful if you are worried about crowding effects.
        Optional; default is None.
    jitter : int
    target_color : int
        color of target. For NumberConfig, default is 'white'.
    distractor_color : int
        color of target. For NumberConfig, default is 'white'.
    target_number : int
    distractor_number : int
    """
    item_bbox_size = attr.ib(validator=optional([instance_of(tuple), check_len_is_two]),
                                 default=(30, 30))
    image_size = attr.ib(validator=optional([instance_of(tuple), check_len_is_two]),
                         default=(227, 227))
    grid_size = attr.ib(validator=optional([instance_of(tuple), check_len_is_two]),
                        default=(5,5))
    border_size = attr.ib(validator=optional([instance_of(tuple), check_len_is_two]),
                          default=None)
    min_center_dist = attr.ib(validator=optional(instance_of(int)), default=None)
    jitter = attr.ib(validator=optional(instance_of(int)), default=5)
    target_color = attr.ib(validator=instance_of(str), default='white')
    distractor_color = attr.ib(validator=instance_of(str), default='white')
    target_number = attr.ib(validator=[instance_of(int), number_validator], default=2)
    distractor_number = attr.ib(validator=[instance_of(int), number_validator], default=5)


@attr.s
class Config:
    """class to represent all sections of config.ini file

    Attributes
    ----------
    general: TrainConfig
        represents [TRAIN] section
    rectangle: RectangleConfig
        represents [RECTANGLE] section
    number: NumberConfig
        represents [NUMBER] section
    """
    general = attr.ib(GeneralConfig)
    rectangle = attr.ib(validator=optional(instance_of(RectangleConfig)), default=None)
    number = attr.ib(validator=optional(instance_of(NumberConfig)), default=None)
