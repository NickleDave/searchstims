"""
test make module
"""
import os
import tempfile
import shutil
import unittest
from glob import glob
import json

import imageio
import numpy as np

from searchstims.config import parse
from searchstims.make import make


HERE = os.path.dirname(__file__)


class TestMake(unittest.TestCase):

    def setUp(self):
        self.test_configs = os.path.join(HERE, 'test_data', 'configs')
        self.tmp_output_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_output_dir)

    def _dirs_got_made(self, config_obj, stim_type):
        for set_size in config_obj.general.set_sizes:
            for target in ('present', 'absent'):
                dir_that_should_exist = os.path.join(
                    self.tmp_output_dir, stim_type, str(set_size), target
                )
                self.assertTrue(os.path.isdir(dir_that_should_exist))
        return True

    def _files_got_made(self, config_obj, stim_type):
        for set_size in config_obj.general.set_sizes:
            for target in ('present', 'absent'):
                if target == 'present':
                    nums = range(config_obj.general.num_target_present // len(config_obj.general.set_sizes))
                elif target == 'absent':
                    nums = range(config_obj.general.num_target_absent // len(config_obj.general.set_sizes))
                for num in nums:
                    if stim_type == 'rectangle':
                        filename = ('redvert_v_greenvert_set_size_{}_'
                                    'target_{}_{}.png'.format(set_size, target, num))
                    elif stim_type == 'number':
                        filename = ('two_v_five_set_size_{}_'
                                    'target_{}_{}.png'.format(set_size, target, num))
                    # use absolute path to save
                    file_that_should_exist = os.path.join(self.tmp_output_dir,
                                                          stim_type,
                                                          str(set_size),
                                                          target,
                                                          filename)

                    self.assertTrue(os.path.isfile(file_that_should_exist))
        return True

    def test_make_rectangle(self):
        rectangle_config_file = os.path.join(self.test_configs, 'test_rectangle_config.ini')
        config_obj = parse(rectangle_config_file)
        config_obj.general.output_dir = self.tmp_output_dir
        make(config_obj)
        self.assertTrue(self._dirs_got_made(config_obj, 'rectangle'))
        self.assertTrue(self._files_got_made(config_obj, 'rectangle'))

    def test_make_number(self):
        number_config_file = os.path.join(self.test_configs, 'test_number_config.ini')
        config_obj = parse(number_config_file)
        config_obj.general.output_dir = self.tmp_output_dir
        make(config_obj)
        self.assertTrue(self._dirs_got_made(config_obj, 'number'))
        self.assertTrue(self._files_got_made(config_obj, 'number'))

    def test_make_number_and_rectangle(self):
        number_config_file = os.path.join(
            self.test_configs, 'test_config_feature_spatial_vgg16.ini'
        )
        config_obj = parse(number_config_file)
        config_obj.general.output_dir = self.tmp_output_dir
        make(config_obj)
        self.assertTrue(self._dirs_got_made(config_obj, 'rectangle'))
        self.assertTrue(self._files_got_made(config_obj, 'rectangle'))
        self.assertTrue(self._dirs_got_made(config_obj, 'number'))
        self.assertTrue(self._files_got_made(config_obj, 'number'))

    def test_when_general_config_has_common_stim_options(self):
        config_file = os.path.join(self.test_configs, 'test_config_general_has_common_stim_options.ini')
        config_obj = parse(config_file)
        config_obj.general.output_dir = self.tmp_output_dir
        make(config_obj)
        self.assertTrue(self._dirs_got_made(config_obj, 'rectangle'))
        self.assertTrue(self._files_got_made(config_obj, 'rectangle'))
        self.assertTrue(self._dirs_got_made(config_obj, 'number'))
        self.assertTrue(self._files_got_made(config_obj, 'number'))

    def test_enforce_unique(self):
        config_file = os.path.join(self.test_configs, 'test_config_enforce_unique.ini')
        config_obj = parse(config_file)
        config_obj.general.output_dir = self.tmp_output_dir
        make(config_obj)
        self.assertTrue(self._dirs_got_made(config_obj, 'rectangle'))
        self.assertTrue(self._files_got_made(config_obj, 'rectangle'))
        fnames_json = glob(os.path.join(self.tmp_output_dir, '*.json'))
        self.assertTrue(len(fnames_json) == 1)
        fnames_json = fnames_json[0]
        with open(fnames_json, 'r') as fp:
            fnames_dict = json.load(fp)
        fnames = [targ_dict['filename']
                  for stim_type, stim_dict in fnames_dict.items()
                  for set_size, set_size_dict in stim_dict.items()
                  for targ, targ_list in set_size_dict.items()
                  for targ_dict in targ_list
                  ]
        imgs = [imageio.imread(os.path.join(self.tmp_output_dir, fname)) for fname in fnames]
        imgs = np.asarray(imgs)
        print("calculating unique images, this might take a minute.")
        uniq_imgs = np.unique(imgs, axis=0)
        self.assertTrue(imgs.shape == uniq_imgs.shape)  # i.e. assert all images are unique


if __name__ == '__main__':
    unittest.main()
