import argparse
import os

from .config import parse
from .make import make


from . import stim_makers

VALID_STIM_SECTIONS = [
    'rectangle',
    'number'
]


COMMON_ARGS = [
        'image_size',
        'border_size',
        'grid_size',
        'min_center_dist',
        'item_bbox_size',
        'jitter',
]


def _get_common_args_from_stim_or_general(stim_config, general_config):
    """helper function that gets arguments from general config if they are not
    specified in the config.ini section corresponding to a visual search stimulus
    
    Parameters
    ----------
    stim_config : RectangleConfig or NumberConfig
        instance of class that represent config.ini section corresponding to a visual search stimulus
    general_config : GeneralConfig
        instance of class that represents config.ini section with general configuration options

    Returns
    -------
    common_args : tuple
        of the arguments listed in searchstims.main.COMMON_ARGS
    """
    common_args = []
    for this_attr in COMMON_ARGS:
        this_arg = getattr(stim_config, this_attr)
        if this_arg is None:
            this_arg = getattr(general_config, this_attr)
        common_args.append(this_arg)
    return tuple(common_args)


def _get_stim_dict(config):
    """for each section in config_obj, if that section is a valid stimulius name,
    then generate a stim_maker for it

    Parameters
    ----------
    config : searchstims.config.classes.Config
        instance of Config returned by parse_config
        after parsing a config.ini file

    """
    general_config = config.general

    stim_dict = {}
    for section in VALID_STIM_SECTIONS:
        if getattr(config, section) is not None:  # because config.section will be None if not defined in config.ini
            stim_config = getattr(config, section)
            (image_size,
             border_size,
             grid_size,
             min_center_dist,
             item_bbox_size,
             jitter) = _get_common_args_from_stim_or_general(stim_config, general_config)

            if section == 'rectangle':
                stim_maker = stim_makers.RectangleStimMaker(target_color=stim_config.target_color,
                                                            distractor_color=stim_config.distractor_color,
                                                            window_size=image_size,
                                                            border_size=border_size,
                                                            grid_size=grid_size,
                                                            min_center_dist=min_center_dist,
                                                            item_bbox_size=item_bbox_size,
                                                            jitter=jitter
                                                            )

            elif section == 'number':
                stim_maker = stim_makers.NumberStimMaker(target_color=stim_config.target_color,
                                                         distractor_color=stim_config.distractor_color,
                                                         window_size=image_size,
                                                         border_size=border_size,
                                                         grid_size=grid_size,
                                                         min_center_dist=min_center_dist,
                                                         item_bbox_size=item_bbox_size,
                                                         jitter=jitter,
                                                         target_number=stim_config.target_number,
                                                         distractor_number=stim_config.distractor_number
                                                         )
            stim_dict[section] = stim_maker

    return stim_dict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('configfile',
                        type=str,
                        help=('filename of config.ini file, e.g.:\n'
                              '$ searchstims ./basic_config.ini\n'
                              'For an example config.ini file, see: '
                              'https://github.com/NickleDave/searchstims'))
    args = parser.parse_args()
    config_file = args.configfile
    if not os.path.isfile(config_file):
        raise FileNotFoundError("Config file {} not found".format(config_file))
    config = parse(config_file)
    stim_dict = _get_stim_dict(config)
    make(root_output_dir=config.general.output_dir,
         stim_dict=stim_dict,
         json_filename=config.general.json_filename,
         num_target_present=config.general.num_target_present,
         num_target_absent=config.general.num_target_absent,
         set_sizes=config.general.set_sizes)


if __name__ == '__main__':
    main()
