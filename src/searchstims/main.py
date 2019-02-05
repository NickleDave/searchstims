import argparse
import os

from .config import parse
from .make import make


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
    config_tuple = parse(config_file)
    make(config_tuple)


if __name__ == '__main__':
    main()
