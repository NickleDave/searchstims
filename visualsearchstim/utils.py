import sys

import pygame
from pygame.locals import *
import numpy as np

pygame.init()

# set up colors
BLACK = ( 0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

def make_rectangle_stim(num_target=1,
					  	num_distractor=7,
					  	target_color=(255, 0, 0),
					  	distractor_color=(0, 255, 0),
					  	grid_size=(5,5),
					  	window_size=(227,227),
					  	rects_width_height=(10,30),
					  	jitter=5):
	"""make visual search stimuli with rectangles
	"""
	if type(num_target) != int:
		raise TypeError('number of targets must be an integer')

	if type(num_distractor) != int:
		raise TypeError('number of distractors must be an integer')

	if not all([type(grid_size_el)==int for grid_size_el in grid_size]):
		raise ValueError('values for grid size must be positive integers')

	if not all([grid_size_el > 0 for grid_size_el in grid_size]):
		raise ValueError('values for grid size must be positive integers')

	if type(jitter) != int:
		raise TypeError('value for jitter must be an integer')

	set_size = num_target + num_distractor

	# make grid, randomly select which cells in grid to use
	grid_x = np.arange(1, grid_size[0]+1)
	grid_y = np.arange(1, grid_size[1]+1)
	xx,yy = np.meshgrid(grid_x, grid_y)
	xx = xx.ravel()
	yy = yy.ravel()
	num_cells = grid_size[0] * grid_size[1]
	cells_to_use = sorted(np.random.choice(np.arange(num_cells),
										   size=set_size,
										   replace=False))
	xx_to_use = xx[cells_to_use]
	yy_to_use = yy[cells_to_use]

	# find centers of cells we're going to use
	cell_width = round(window_size[0] / grid_size[0])
	cell_x_end = np.arange(1, grid_size[0]+1) * cell_width
	cell_x_center = round((window_size[0] / grid_size[0]) / 2)
	xx_to_use_ctr = (xx_to_use * cell_width) - cell_x_center
	cell_height = round(window_size[1] / grid_size[1])
	cell_y_end = np.arange(1, grid_size[1]+1) * cell_height
	cell_y_center = round((window_size[1] / grid_size[1]) / 2)
	yy_to_use_ctr = (yy_to_use * cell_height) - cell_y_center

	# add jitter to those points
	jitter_high = jitter // 2
	jitter_low = -jitter_high
	if jitter % 2 == 0:  # if even
		# have to account for zero at center of jitter range
		# (otherwise range would be jitter + 1)
		# (Not a problem when doing floor division on odd #s)
		coin_flip = np.random.choice([0,1])
		if coin_flip == 0:
			jitter_low += 1
		elif coin_flip == 1:
			jitter_high -= 1
	jitter_range = np.arange(jitter_low,jitter_high+1)

	x_jitter = np.random.choice(jitter_range, size=xx_to_use.size)
	xx_to_use_ctr += x_jitter
	y_jitter = np.random.choice(jitter_range, size=yy_to_use.size)
	yy_to_use_ctr += y_jitter

	# set up window
	DISPLAYSURF = pygame.display.set_mode(window_size, 0, 32)

	# draw on surface object
	DISPLAYSURF.fill(BLACK)
	target_inds = np.random.choice(np.arange(set_size), size=num_target).tolist()
	rects = []
	for item in range(set_size):
		rect_tuple = (0, 0) + rects_width_height
		rect_to_draw = Rect(rect_tuple)
		rect_to_draw.center = (xx_to_use_ctr[item], yy_to_use_ctr[item])
		if item in target_inds:
			curr_rect = pygame.draw.rect(DISPLAYSURF, target_color, rect_to_draw)
		else:
			curr_rect = pygame.draw.rect(DISPLAYSURF, distractor_color, rect_to_draw)
		rects.append(curr_rect)

	pygame.display.update()
	return DISPLAYSURF

if __name__ == '__main__':
	make_rectangle_stim()