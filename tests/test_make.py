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


class TestMain(unittest.TestCase):

    def setUp(self):
        self.test_configs = os.path.join(HERE, 'test_data', 'configs')
        self.tmp_output_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_output_dir)

    def test_make_rectangle(self):
        rectangle_config_file = os.path.join(self.test_configs, 'test_rectangle_config.ini')
        config_obj = parse(rectangle_config_file)
        config_obj.general.output_dir = self.tmp_output_dir
        make(config_obj)

    def test_make_number(self):
        number_config_file = os.path.join(self.test_configs, 'test_number_config.ini')
        config_obj = parse(number_config_file)
        config_obj.general.output_dir = self.tmp_output_dir
        make(config_obj)

    def test_make_number_and_rectangle(self):
        number_config_file = os.path.join(
            self.test_configs, 'test_config_feature_spatial_vgg16.ini'
        )
        config_obj = parse(number_config_file)
        config_obj.general.output_dir = self.tmp_output_dir
        make(config_obj)


if __name__ == '__main__':
    unittest.main()
