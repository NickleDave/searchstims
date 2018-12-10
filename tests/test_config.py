"""
test config module
"""
import os
from configparser import ConfigParser
import unittest

import searchstims.config


HERE = os.path.dirname(os.path.abspath(__file__))


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_configs = os.path.join(HERE, '..', 'doc', 'configs')
        self.default_config_file = os.path.join(HERE, '..', 'src', 'searchstims', 'default.ini')
        self.default_config = ConfigParser()
        self.default_config.read(self.default_config_file)

    def tuple_fields_equal_ConfigParser_sections(self, config_tuple, config_parser_obj):
        if list(config_tuple._fields) == config_parser_obj.sections():
            return True
        else:
            return False

    def all_declared_config_options_are_tuple_fields(self, config_tuple, config_parser_obj):
        tuple_dict = config_tuple._asdict()
        fields_equal_to_options = []
        for section in config_parser_obj.sections():
            declared_options = config_parser_obj.options(section)
            section_tuple = tuple_dict[section]
            section_tuple_fields = sorted(list(section_tuple._fields))
            if all([option in section_tuple_fields for option in declared_options]):
                fields_equal_to_options.append(True)
            else:
                fields_equal_to_options.append(False)

        if all(fields_equal_to_options):
            return True
        else:
            return False

    def all_undeclared_config_options_are_tuple_fields(self, config_tuple, config_parser_obj):
        # make sure that the config tuple has fields that are declared in the default config
        # for a given section even if the user didn't declare them
        tuple_dict = config_tuple._asdict()
        undeclared_options_are_fields = []
        for section in config_parser_obj.sections():
            declared_options = set(config_parser_obj.options(section))
            default_options = set(self.default_config.options(section))
            undeclared_options = list(default_options - declared_options)
            section_tuple = tuple_dict[section]
            section_tuple_fields = sorted(list(section_tuple._fields))
            if all([option in section_tuple_fields for option in undeclared_options]):
                undeclared_options_are_fields.append(True)
            else:
                undeclared_options_are_fields.append(False)

        if all(undeclared_options_are_fields):
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
        self.assertTrue(self.all_declared_config_options_are_tuple_fields(basic_config_tup,
                                                                          basic_config))
        self.assertTrue(self.all_undeclared_config_options_are_tuple_fields(basic_config_tup,
                                                                            basic_config))

    def test_parse_rectangle_config(self):
        # get file we need and load into ConfigParser instance to use for tests
        rectangle_config_file = os.path.join(self.test_configs, 'rectangle_config.ini')
        rectangle_config = ConfigParser()
        rectangle_config.read(rectangle_config_file)

        # now run through parser
        rectangle_config_tup = searchstims.config.parse(rectangle_config_file)

        self.assertTrue(self.tuple_fields_equal_ConfigParser_sections(rectangle_config_tup,
                                                                      rectangle_config))
        self.assertTrue(self.all_declared_config_options_are_tuple_fields(rectangle_config_tup,
                                                                          rectangle_config))
        self.assertTrue(self.all_undeclared_config_options_are_tuple_fields(rectangle_config_tup,
                                                                            rectangle_config))

    def test_config_with_multiple_stim_raises(self):
        # make sure it raises an error if we use a config file with more than one section
        # that declares options for search stimuli, i.e. has a [rectangle] and a [number] section
        # Use the default config to check this because it declares defaults for all possible
        # sections (never gets used as a config itself)
        with self.assertRaises(ValueError):
            searchstims.config.parse(self.default_config_file)


if __name__ == '__main__':
    unittest.main()
