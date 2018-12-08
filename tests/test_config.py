"""
test config module
"""
import os
import shutil
from configparser import ConfigParser
import unittest

import searchstims.config


HERE = os.path.dirname(os.path.abspath(__file__))


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_configs = os.path.join(HERE, 'test_data', 'configs')

    def tuple_fields_equal_ConfigParser_sections(self, config_tuple, config_parser_obj):
        if list(config_tuple._fields) == config_parser_obj.sections():
            return True
        else:
            return False

    def tuple_section_fields_equal_ConfigParser_options(self, config_tuple, config_parser_obj):
        tuple_sections = sorted(list(config_tuple._fields))
        parser_sections = sorted(config_parser_obj.sections())
        tuple_dict = config_tuple._asdict()
        fields_equal_to_options = []
        for tup_sect, parse_sect in zip(tuple_sections, parser_sections):
            section_tuple = tuple_dict[tup_sect]
            section_tuple_fields = sorted(list(section_tuple._fields))
            section_options = sorted(config_parser_obj.options(parse_sect))
            if section_tuple_fields == section_options:
                fields_equal_to_options.append(True)
            else:
                fields_equal_to_options.append(False)

        if all(fields_equal_to_options):
            return True
        else:
            return False

    def test_parse_basic_config(self):
        # get file we need and load into ConfigParser instance to use for tests
        basic_config_file = os.path.join(self.test_configs, 'basic_config.ini')
        basic_config = ConfigParser()
        basic_config.read(basic_config_file)

        # now run through parser
        basic_config_tup = searchstims.config.parse(basic_config_file)

        self.assertTrue(self.tuple_fields_equal_ConfigParser_sections(basic_config_tup,
                                                                      basic_config))
        self.assertTrue(self.tuple_section_fields_equal_ConfigParser_options(basic_config_tup,
                                                                             basic_config))


if __name__ == '__main__':
    unittest.main()
