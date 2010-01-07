import pygame

import data

OBS_BRICK_TEX = None
OBS_CARPET_TEX = None
OBS_DENIM_TEX = None
OBS_TWEED_TEX = None

LYR_COTTON_TEX = None
LYR_EXPLOSION_TEX = None
LYR_FEATHER_TEX = None
LYR_METAL_TEX = None
LYR_SLIME_1_TEX = None
LYR_SLIME_2_TEX = None
LYR_SLIME_3_TEX = None
LYR_TAR_TEX = None

_initialized = False
def init():
	global _initialized
	if _initialized:
		return
	else:
		_initialized = True
		
	global OBS_BRICK_TEX
	OBS_BRICK_TEX = pygame.image.load(data.filepath('texture-obstacle-brick.jpg'))
	global OBS_CARPET_TEX
	OBS_CARPET_TEX = pygame.image.load(data.filepath('texture-obstacle-carpet.jpg'))
	global OBS_DENIM_TEX
	OBS_DENIM_TEX = pygame.image.load(data.filepath('texture-obstacle-denim.jpg'))
	global OBS_TWEED_TEX
	OBS_TWEED_TEX = pygame.image.load(data.filepath('texture-obstacle-tweed.jpg'))
	
	global LYR_COTTON_TEX
	LYR_COTTON_TEX = pygame.image.load(data.filepath('texture-cotton.jpg'))
	global LYR_EXPLOSION_TEX
	LYR_EXPLOSION_TEX = pygame.image.load(data.filepath('texture-explosion.jpg'))
	global LYR_FEATHER_TEX
	LYR_FEATHER_TEX = pygame.image.load(data.filepath('texture-feather.jpg'))
	global LYR_METAL_TEX
	LYR_METAL_TEX = pygame.image.load(data.filepath('texture-metal.jpg'))
	global LYR_SLIME_1_TEX
	LYR_SLIME_1_TEX = pygame.image.load(data.filepath('texture-slime-1.jpg'))
	global LYR_SLIME_2_TEX
	LYR_SLIME_2_TEX = pygame.image.load(data.filepath('texture-slime-2.jpg'))
	global LYR_SLIME_3_TEX
	LYR_SLIME_3_TEX = pygame.image.load(data.filepath('texture-slime-3.jpg'))
	global LYR_TAR_TEX
	LYR_TAR_TEX = pygame.image.load(data.filepath('texture-tar.jpg'))
	
