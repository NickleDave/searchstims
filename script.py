import pygame

from visualsearchstim.utils import make_rectangle_stim

if __name__ == '__main__':
	num_target_present = 10
	num_target_absent = 10
	total_set_size = 8

	num_distractors_target_present = total_set_size - 1
	for i in range(num_target_present):
		filename = 'feature_search_stimulus_target_present_{}.png'.format(i)
		surface = make_rectangle_stim(num_distractor=num_distractors_target_present)
		pygame.image.save(surface, filename)

	num_distractors_target_absent = total_set_size
	for i in range(num_target_absent):
		filename = 'feature_search_stimulus_target_absent_{}.png'.format(i)
		surface = make_rectangle_stim(num_target=0,
									  num_distractor=num_distractors_target_absent)
		pygame.image.save(surface, filename)