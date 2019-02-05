"""
test make module
"""
import os
import tempfile
import shutil
from configparser import ConfigParser
import unittest

from searchstims.config import parse
from searchstims.make import make


HERE = os.path.dirname(__file__)
TEST_CONFIGS = os.path.join(HERE, 'test_data', 'config')


class TestMain(unittest.TestCase):

    def setUp(self):
        self.tmp_output_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_output_dir)

    def test_make_number(self):
        config = ConfigParser()
        config.add_section('general')
        config['general']['num_target_present'] = '25'
        config['general']['num_target_absent'] = '25'
        config['general']['set_sizes'] = '[1, 2, 4, 6, 8]'
        config['general']['output_dir'] = self.tmp_output_dir
        config['general']['json_filename'] = 'filenames_by_set_size_and_target.json'
        config.add_section('number')
        config['number']['rects_width_height'] = '(30,30)'
        config_tup = parse(config=config)
        make(config_tup)

    def test_make_rectangle(self):
        config = ConfigParser()
        config.add_section('general')
        config['general']['num_target_present'] = '25'
        config['general']['num_target_absent'] = '25'
        config['general']['set_sizes'] = '[1, 2, 4, 6, 8]'
        config['general']['output_dir'] = self.tmp_output_dir
        config['general']['json_filename'] = 'filenames_by_set_size_and_target.json'
        config.add_section('rectangle')
        config['rectangle']['rects_width_height'] = '(10,30)'
        config_tup = parse(config=config)
        make(config_tup)


if __name__ == '__main__':
    unittest.main()
