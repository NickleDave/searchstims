"""
test make module
"""
import csv
import os
import tempfile
import shutil
import unittest
from glob import glob

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

    def _files_got_made_num_target_present_absent_list(self, config, stim_type,
                                                       num_target_present, num_target_absent):
        for set_size, num_imgs_present, num_imgs_absent in zip(
                config.general.set_sizes, num_target_present, num_target_absent):
            for target in ('present', 'absent'):
                if target == 'present':
                    nums = range(num_imgs_present)
                elif target == 'absent':
                    nums = range(num_imgs_absent)
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

    def test_make_RVvGV(self):
        RVvGV_config_file = os.path.join(self.test_configs, 'test_RVvGV_config.ini')
        config = parse(RVvGV_config_file)
        config.general.output_dir = self.tmp_output_dir
        stim_dict = _get_stim_dict(config)

        make(root_output_dir=config.general.output_dir,
             stim_dict=stim_dict,
             csv_filename=config.general.csv_filename,
             num_target_present=config.general.num_target_present,
             num_target_absent=config.general.num_target_absent,
             set_sizes=config.general.set_sizes)

        self.assertTrue(self._dirs_got_made(config, 'RVvGV'))
        self.assertTrue(self._files_got_made(config, 'RVvGV'))

    def test_make_2_v_5(self):
        Two_v_Five_config_file = os.path.join(self.test_configs, 'test_2_v_5_config.ini')
        config = parse(Two_v_Five_config_file)
        config.general.output_dir = self.tmp_output_dir
        stim_dict = _get_stim_dict(config)

        make(root_output_dir=config.general.output_dir,
             stim_dict=stim_dict,
             csv_filename=config.general.csv_filename,
             num_target_present=config.general.num_target_present,
             num_target_absent=config.general.num_target_absent,
             set_sizes=config.general.set_sizes)

        self.assertTrue(self._dirs_got_made(config, '2_v_5'))
        self.assertTrue(self._files_got_made(config, '2_v_5'))

    def test_make_Two_v_Five_and_RVvGV(self):
        Two_v_Five_config_file = os.path.join(
            self.test_configs, 'test_config_feature_spatial_vgg16.ini'
        )
        config = parse(Two_v_Five_config_file)
        config.general.output_dir = self.tmp_output_dir
        stim_dict = _get_stim_dict(config)

        make(root_output_dir=config.general.output_dir,
             stim_dict=stim_dict,
             csv_filename=config.general.csv_filename,
             num_target_present=config.general.num_target_present,
             num_target_absent=config.general.num_target_absent,
             set_sizes=config.general.set_sizes)

        self.assertTrue(self._dirs_got_made(config, 'RVvGV'))
        self.assertTrue(self._files_got_made(config, 'RVvGV'))
        self.assertTrue(self._dirs_got_made(config, '2_v_5'))
        self.assertTrue(self._files_got_made(config, '2_v_5'))

    def test_when_general_config_has_common_stim_options(self):
        config_file = os.path.join(self.test_configs, 'test_config_general_has_common_stim_options.ini')
        config = parse(config_file)
        config.general.output_dir = self.tmp_output_dir
        stim_dict = _get_stim_dict(config)

        make(root_output_dir=config.general.output_dir,
             stim_dict=stim_dict,
             csv_filename=config.general.csv_filename,
             num_target_present=config.general.num_target_present,
             num_target_absent=config.general.num_target_absent,
             set_sizes=config.general.set_sizes)

        self.assertTrue(self._dirs_got_made(config, 'RVvGV'))
        self.assertTrue(self._files_got_made(config, 'RVvGV'))
        self.assertTrue(self._dirs_got_made(config, '2_v_5'))
        self.assertTrue(self._files_got_made(config, '2_v_5'))

    def test_enforce_unique(self):
        config_file = os.path.join(self.test_configs, 'test_config_enforce_unique.ini')
        config = parse(config_file)
        config.general.output_dir = self.tmp_output_dir
        stim_dict = _get_stim_dict(config)

        make(root_output_dir=config.general.output_dir,
             stim_dict=stim_dict,
             csv_filename=config.general.csv_filename,
             num_target_present=config.general.num_target_present,
             num_target_absent=config.general.num_target_absent,
             set_sizes=config.general.set_sizes)

        self.assertTrue(self._dirs_got_made(config, 'RVvGV'))
        self.assertTrue(self._files_got_made(config, 'RVvGV'))
        fnames_csv = glob(os.path.join(self.tmp_output_dir, '*.csv'))
        self.assertTrue(len(fnames_csv) == 1)
        fnames_csv = fnames_csv[0]
        with open(fnames_csv, 'r') as fp:
            reader = csv.DictReader(fp)
            fnames = [row['img_file'] for row in reader]
        imgs = [imageio.imread(os.path.join(self.tmp_output_dir, fname)) for fname in fnames]
        imgs = np.asarray(imgs)
        print("calculating unique images, this might take a minute.")
        uniq_imgs = np.unique(imgs, axis=0)
        self.assertTrue(imgs.shape == uniq_imgs.shape)  # i.e. assert all images are unique

    def test_num_target_present_absent_are_list(self):
        config_file = os.path.join(self.test_configs, 'test_RVvGV_config.ini')
        config = parse(config_file)
        config.general.output_dir = self.tmp_output_dir
        stim_dict = _get_stim_dict(config)

        num_target_present = [10, 20, 40, 60, 80]
        num_target_absent = [10, 20, 40, 60, 80]

        make(root_output_dir=config.general.output_dir,
             stim_dict=stim_dict,
             csv_filename=config.general.csv_filename,
             num_target_present=num_target_present,
             num_target_absent=num_target_absent,
             set_sizes=config.general.set_sizes)

        self.assertTrue(self._dirs_got_made(config, 'RVvGV'))
        self.assertTrue(self._files_got_made_num_target_present_absent_list(
            config, 'RVvGV', num_target_present, num_target_absent))


if __name__ == '__main__':
    unittest.main()
