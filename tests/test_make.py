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
from searchstims.main import _get_stim_dict


HERE = os.path.dirname(__file__)


class TestMake(unittest.TestCase):

    def setUp(self):
        self.test_configs = os.path.join(HERE, 'test_data', 'configs')
        self.tmp_output_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_output_dir)

    def _dirs_got_made(self, config, stim_type):
        for set_size in config.general.set_sizes:
            for target in ('present', 'absent'):
                dir_that_should_exist = os.path.join(
                    self.tmp_output_dir, stim_type, str(set_size), target
                )
                self.assertTrue(os.path.isdir(dir_that_should_exist))
        return True

    def _files_got_made(self, config, stim_type):
        for set_size in config.general.set_sizes:
            for target in ('present', 'absent'):
                if target == 'present':
                    nums = range(config.general.num_target_present // len(config.general.set_sizes))
                elif target == 'absent':
                    nums = range(config.general.num_target_absent // len(config.general.set_sizes))
                for num in nums:
                    filename = f'{stim_type}_set_size_{set_size}_target_{target}_{num}.png'
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
        config = parse(rectangle_config_file)
        config.general.output_dir = self.tmp_output_dir
        stim_dict = _get_stim_dict(config)

        make(root_output_dir=config.general.output_dir,
             stim_dict=stim_dict,
             json_filename=config.general.json_filename,
             num_target_present=config.general.num_target_present,
             num_target_absent=config.general.num_target_absent,
             set_sizes=config.general.set_sizes)

        self.assertTrue(self._dirs_got_made(config, 'rectangle'))
        self.assertTrue(self._files_got_made(config, 'rectangle'))

    def test_make_number(self):
        number_config_file = os.path.join(self.test_configs, 'test_number_config.ini')
        config = parse(number_config_file)
        config.general.output_dir = self.tmp_output_dir
        stim_dict = _get_stim_dict(config)

        make(root_output_dir=config.general.output_dir,
             stim_dict=stim_dict,
             json_filename=config.general.json_filename,
             num_target_present=config.general.num_target_present,
             num_target_absent=config.general.num_target_absent,
             set_sizes=config.general.set_sizes)

        self.assertTrue(self._dirs_got_made(config, 'number'))
        self.assertTrue(self._files_got_made(config, 'number'))

    def test_make_number_and_rectangle(self):
        number_config_file = os.path.join(
            self.test_configs, 'test_config_feature_spatial_vgg16.ini'
        )
        config = parse(number_config_file)
        config.general.output_dir = self.tmp_output_dir
        stim_dict = _get_stim_dict(config)

        make(root_output_dir=config.general.output_dir,
             stim_dict=stim_dict,
             json_filename=config.general.json_filename,
             num_target_present=config.general.num_target_present,
             num_target_absent=config.general.num_target_absent,
             set_sizes=config.general.set_sizes)

        self.assertTrue(self._dirs_got_made(config, 'rectangle'))
        self.assertTrue(self._files_got_made(config, 'rectangle'))
        self.assertTrue(self._dirs_got_made(config, 'number'))
        self.assertTrue(self._files_got_made(config, 'number'))

    def test_when_general_config_has_common_stim_options(self):
        config_file = os.path.join(self.test_configs, 'test_config_general_has_common_stim_options.ini')
        config = parse(config_file)
        config.general.output_dir = self.tmp_output_dir
        stim_dict = _get_stim_dict(config)

        make(root_output_dir=config.general.output_dir,
             stim_dict=stim_dict,
             json_filename=config.general.json_filename,
             num_target_present=config.general.num_target_present,
             num_target_absent=config.general.num_target_absent,
             set_sizes=config.general.set_sizes)

        self.assertTrue(self._dirs_got_made(config, 'rectangle'))
        self.assertTrue(self._files_got_made(config, 'rectangle'))
        self.assertTrue(self._dirs_got_made(config, 'number'))
        self.assertTrue(self._files_got_made(config, 'number'))

    def test_enforce_unique(self):
        config_file = os.path.join(self.test_configs, 'test_config_enforce_unique.ini')
        config = parse(config_file)
        config.general.output_dir = self.tmp_output_dir
        stim_dict = _get_stim_dict(config)

        make(root_output_dir=config.general.output_dir,
             stim_dict=stim_dict,
             json_filename=config.general.json_filename,
             num_target_present=config.general.num_target_present,
             num_target_absent=config.general.num_target_absent,
             set_sizes=config.general.set_sizes)

        self.assertTrue(self._dirs_got_made(config, 'rectangle'))
        self.assertTrue(self._files_got_made(config, 'rectangle'))
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
