import os

import pygame

from visualsearchstim.utils import make_rectangle_stim

if __name__ == '__main__':

    output_dir = os.path.join('.', 'output')
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    num_target_present = 4800
    num_target_absent = 4800
    set_sizes = [1, 2, 4, 6, 8]

    for set_size in set_sizes:
        num_distractors = set_size - 1
        for i in range(num_target_present // len(set_sizes)):
            filename = ('redvert_v_greenvert_set_size_{}_'
                        'target_present_{}.png'.format(set_size, i))
            filename = os.path.join(output_dir, filename)
            surface = make_rectangle_stim(set_size=set_size,
                                          num_target=1)
            pygame.image.save(surface, filename)

        num_distractors_target_absent = set_size
        for i in range(num_target_absent // len(set_sizes)):
            filename = ('redvert_v_greenvert_set_size_{}_'
                        'target_absent_{}.png'.format(set_size, i))
            filename = os.path.join(output_dir, filename)
            surface = make_rectangle_stim(set_size=set_size,
                                          num_target=0)
            pygame.image.save(surface, filename)
