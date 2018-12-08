"""
test config module
"""
import os
import tempfile
import shutil
from configparser import ConfigParser
import unittest

import searchstims.config


HERE = os.path.dirname(os.path.abspath(__file__))


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_configs = os.path.join(HERE, 'test_data', 'config')
        self.tmp_output_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_output_dir)

    def test_parse_basic_config(self):
        # get file we need and load into ConfigParser instance to use for tests
        basic_config_file = os.path.join(self.test_configs, 'basic_config.ini')
        basic_config = ConfigParser()
        basic_config.read(basic_config_file)

        # now run through parser
        basic_config_tup = searchstims.config.parse(basic_config_file)

        sections = [key for key in list(config.keys()) if key != 'DEFAULT']
        self.assertTrue(basic_config_tup._fields == sections)


if __name == '__main__':
    unittest.main()
