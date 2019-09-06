import csv
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import searchstims

TEST_DIR = Path(__file__).parent
TEST_DATA_DIR = TEST_DIR.joinpath('test_data')


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.tmp_output_dir = tempfile.mkdtemp()
        json_filename = 'alexnet_train_multiple_stims.json'
        json_path = TEST_DATA_DIR.joinpath('json', json_filename)
        self.json_path = shutil.copyfile(json_path,
                                         Path(self.tmp_output_dir).joinpath(
                                             json_path.name))

    def test_make_csv(self):
        num_imgs = 10
        img_nums = list(range(num_imgs))
        root_output_dir = self.tmp_output_dir
        to_csv = {
            'stimulus': ('RVvGV', '2_v_5'),
            'set_size': (1, 2, 4, 8),
            'target_condition': ('present', 'absent'),
            'img_num': img_nums,
        }

        rows = []
        for stimulus in to_csv['stimulus']:
            for set_size in to_csv['set_size']:
                for target_condition in to_csv['target_condition']:
                    for img_num in img_nums:
                        img_file = (
                            f'{stimulus}_set_size_{set_size}_target_{target_condition}'
                            f'_{img_num}.png'
                        )
                        meta_file = img_file.replace('png', 'meta.json')
                        row = [stimulus,
                               set_size,
                               target_condition,
                               img_num,
                               root_output_dir,
                               img_file,
                               meta_file]
                        rows.append(row)

        csv_filename = str(Path(root_output_dir).joinpath('test.csv'))
        searchstims.utils.make_csv(rows, csv_filename)

        with open(csv_filename) as f:
            reader = csv.DictReader(f)
            self.assertTrue(
                reader.fieldnames == searchstims.utils.FIELDNAMES
            )
            num_rows = 0
            for row in reader:
                num_rows += 1
                row = searchstims.utils.SearchStimulus.cast_row(row)
                for key, val in row.items():
                    if key in ['stimulus', 'set_size', 'target_condition', 'img_num']:
                        self.assertTrue(
                            val in to_csv[key]
                        )
                    elif key == 'root_output_dir':
                        self.assertTrue(val == root_output_dir)
                    elif key == 'img_file' or key == 'meta_file':
                        stem = (f"{row['stimulus']}_set_size_{row['set_size']}_target_"
                                f"{row['target_condition']}_{row['img_num']}")
                        if key == 'img_file':
                            self.assertTrue(val == stem + '.png')
                        elif key == 'meta_file':
                            self.assertTrue(val == stem + '.meta.json')
            expected_num_rows = len(img_nums) * len(to_csv['stimulus']) * \
                                len(to_csv['set_size']) * len(to_csv['target_condition'])
            self.assertTrue(num_rows == expected_num_rows)

    def test_json_to_csv(self):
        with open(self.json_path) as fp:
            metadict = json.load(fp)

        # make needed sub-directories (that would already be made by searchstims.make)
        # and also count the number of meta.json files we expect to make
        root_output_dir = self.tmp_output_dir
        num_expected_meta_json_files = 0
        for stimulus, stim_dict in metadict.items():
            for set_size, set_size_dict in stim_dict.items():
                for target_condition, list_meta_dict in set_size_dict.items():
                    meta_dict_parent = Path(root_output_dir).joinpath(stimulus,
                                                                      set_size,
                                                                      target_condition)
                    if not meta_dict_parent.is_dir():
                        # make directory to avoid spurious 'FileNotFoundError'
                        # which wouldn't happen in real life because searchstims.make
                        # will have made the parent directories on its own
                        meta_dict_parent.mkdir(parents=True)
                    for meta_dict in list_meta_dict:
                        # count the number of meta json files we expect
                        num_expected_meta_json_files += 1

        searchstims.utils.json_to_csv(self.json_path, root_output_dir)

        expected_csv = Path(root_output_dir).joinpath(
            self.json_path.name.replace('json', 'csv')
        )
        self.assertTrue(
            expected_csv.exists()
        )

        meta_json_files = list(Path(root_output_dir).glob('**/*.meta.json'))
        self.assertTrue(
            len(meta_json_files) == num_expected_meta_json_files
        )


if __name__ == '__main__':
    unittest.main()
