"""test config module"""
import os
from configparser import ConfigParser
import unittest
import tempfile

import searchstims.config
from searchstims.config.parse import SECTION_CONFIG_ATTRIB_MAP

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
        set to default by searchstims.config.parse

        Parameters
        ----------
        config_parser : ConfigParser
            with config.ini file loaded into it
        config_obj : searchstims.config.classes.Config
            returned by searchstims.config.parse
        section_name_list : list
            of str, names of sections to compare to default
        """
        option_was_set_to_default = []
        for section in section_name_list:
            # get name of attribute on Config object
            section_attr_name = SECTION_CONFIG_ATTRIB_MAP[section]
            section_obj = getattr(config_obj, section_attr_name)
            default_section_obj = getattr(self.default_config_obj, section_attr_name)
            # here don't use attribute name, use name in config.ini file
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

    def test_parse_RVvGV_config(self):
        # get file we need and load into ConfigParser instance to use for tests
        RVvGV_config_file = os.path.join(self.test_configs, 'test_RVvGV_config.ini')
        RVvGV_config = ConfigParser()
        RVvGV_config.read(RVvGV_config_file)
        RVvGV_config_obj = searchstims.config.parse(RVvGV_config_file)

        self.assertTrue(hasattr(RVvGV_config_obj, 'general'))
        self.assertTrue(hasattr(RVvGV_config_obj, 'RVvGV'))
        self.assertTrue(RVvGV_config_obj.Two_v_Five is None)
        self.assertTrue(self._test_defaults_set_correctly(
            RVvGV_config, RVvGV_config_obj, ['general', 'RVvGV']
        ))

    def test_parse_Two_v_Five_config(self):
        # get file we need and load into ConfigParser instance to use for tests
        Two_v_Five_config_file = os.path.join(self.test_configs, 'test_2_v_5_config.ini')
        Two_v_Five_config = ConfigParser()
        Two_v_Five_config.read(Two_v_Five_config_file)
        Two_v_Five_config_obj = searchstims.config.parse(Two_v_Five_config_file)

        self.assertTrue(hasattr(Two_v_Five_config_obj, 'general'))
        self.assertTrue(hasattr(Two_v_Five_config_obj, 'Two_v_Five'))
        self.assertTrue(Two_v_Five_config_obj.RVvGV is None)

        self.assertTrue(self._test_defaults_set_correctly(
            Two_v_Five_config, Two_v_Five_config_obj, ['general', '2_v_5']
        ))

    def test_parse_RVvGV_Two_v_Five_config(self):
        # get file we need and load into ConfigParser instance to use for tests
        config_file = os.path.join(self.test_configs, 'test_config_feature_spatial_vgg16.ini')
        config = ConfigParser()
        config.read(config_file)
        config_obj = searchstims.config.parse(config_file)

        self.assertTrue(hasattr(config_obj, 'general'))
        self.assertTrue(hasattr(config_obj, 'RVvGV'))
        self.assertTrue(hasattr(config_obj, 'Two_v_Five'))

        self.assertTrue(self._test_defaults_set_correctly(
            config, config_obj, ['general', 'RVvGV', '2_v_5']
        ))


if __name__ == '__main__':
    unittest.main()
