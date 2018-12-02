"""
test main module
"""
import os
import tempfile
import shutil
from configparser import ConfigParser
import unittest

import searchstims.main


HERE = os.path.dirname(__file__)
TEST_CONFIGS = os.path.join(HERE, 'test_data', 'config')


class TestMain(unittest.TestCase):

    def setUp(self):
        self.tmp_output_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_output_dir)

    def test_parse_config(self):


    def test_make_number(self):
        config = ConfigParser()
        config.add_section('config')
        config['config']['num_target_present'] = 25
        config['num_target_absent'] = 25
        config['set_sizes'] = [1, 2, 4, 6, 8]
        config['output_dir'] = self.tmp_output_dir
        config['json_filename'] = 'filenames_by_set_size_and_target.json'
        config['stimulus'] = 'number'
        searchstims.main.make(config)

    def test_make_rectangle(self):
        config = ConfigParser()
        config.add_section('config')
        config['config']['num_target_present'] = 25
        config['num_target_absent'] = 25
        config['set_sizes'] = [1, 2, 4, 6, 8]
        config['output_dir'] = self.tmp_output_dir
        config['json_filename'] = 'filenames_by_set_size_and_target.json'
        config['stimulus'] = 'rectangle'
        searchstims.main.make(config)


if __name__ == '__main__':
    unittest.main()
