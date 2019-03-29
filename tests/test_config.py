"""test config module"""
import os
from configparser import ConfigParser
import unittest
import tempfile

import searchstims.config


HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_FILE = os.path.join(
            HERE, '..', 'src', 'searchstims', 'config', 'default.ini'
)


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_configs = os.path.join(HERE, 'test_data', 'configs')
        self.default_config = ConfigParser()
        self.default_config.read(DEFAULT_CONFIG_FILE)
        self.default_config_obj = searchstims.config.parse(DEFAULT_CONFIG_FILE)

    def _test_defaults_set_correctly(self,
                                     config_parser,
                                     config_obj,
                                     section_name_list):
        """helper function that checks all option not set by user are
        set to default by searchstims.config.parse"""
        option_was_set_to_default = []
        for section in section_name_list:
            section_obj = getattr(config_obj, section)
            default_section_obj = getattr(self.default_config_obj, section)
            default_section = self.default_config[section]
            config_section = config_parser[section]
            for option in default_section.keys():
                if option not in config_section:
                    # if user did not set this option
                    option_was_set_to_default.append(
                        # make sure it equals default
                        getattr(section_obj, option) == getattr(default_section_obj, option)
                    )

        if all(option_was_set_to_default):
            return True
        else:
            return False


    def test_no_general_section_raises_error(self):
        tmp_dir = tempfile.mkdtemp()
        default_config_copy = ConfigParser()
        default_config_copy.read_dict(self.default_config)
        default_config_copy.remove_section('general')
        no_general_config_file = os.path.join(tmp_dir, 'no_general_config.ini')
        with open(no_general_config_file, 'w') as f:
            default_config_copy.write(f)
        with self.assertRaises(ValueError):
            searchstims.config.parse(config_file=no_general_config_file)

    def test_parse_rectangle_config(self):
        # get file we need and load into ConfigParser instance to use for tests
        rectangle_config_file = os.path.join(self.test_configs, 'rectangle_config.ini')
        rectangle_config = ConfigParser()
        rectangle_config.read(rectangle_config_file)
        rectangle_config_obj = searchstims.config.parse(rectangle_config_file)

        self.assertTrue(hasattr(rectangle_config_obj, 'general'))
        self.assertTrue(hasattr(rectangle_config_obj, 'rectangle'))
        self.assertTrue(rectangle_config_obj.number is None)
        self.assertTrue(self._test_defaults_set_correctly(
            rectangle_config, rectangle_config_obj, ['general', 'rectangle']
        ))

    def test_parse_number_config(self):
        # get file we need and load into ConfigParser instance to use for tests
        number_config_file = os.path.join(self.test_configs, 'number_config.ini')
        number_config = ConfigParser()
        number_config.read(number_config_file)
        number_config_obj = searchstims.config.parse(number_config_file)

        self.assertTrue(hasattr(number_config_obj, 'general'))
        self.assertTrue(hasattr(number_config_obj, 'number'))
        self.assertTrue(number_config_obj.rectangle is None)

        self.assertTrue(self._test_defaults_set_correctly(
            number_config, number_config_obj, ['general', 'number']
        ))

    def test_parse_rectangle_number_config(self):
        # get file we need and load into ConfigParser instance to use for tests
        config_file = os.path.join(self.test_configs, 'config_feature_spatial_vgg16.ini')
        config = ConfigParser()
        config.read(config_file)
        config_obj = searchstims.config.parse(config_file)

        self.assertTrue(hasattr(config_obj, 'general'))
        self.assertTrue(hasattr(config_obj, 'rectangle'))
        self.assertTrue(hasattr(config_obj, 'number'))

        self.assertTrue(self._test_defaults_set_correctly(
            config, config_obj, ['general', 'rectangle', 'number']
        ))


if __name__ == '__main__':
    unittest.main()
