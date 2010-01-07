#! /usr/bin/env python

import locale
locale.setlocale(locale.LC_ALL, "")

import pygame
pygame.mixer.pre_init(22050, -16, 2, 1024)
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Angel-G")

import src.data
pygame.mixer.music.load(src.data.filepath('sound-music.ogg'))
pygame.mixer.music.set_volume(0.5)

import src.textures
import src.sprite
_player_torso_blitmask = pygame.image.load(src.data.filepath('player-blitmask-torso.png'))
_player_wings_blitmask_1 = pygame.image.load(src.data.filepath('player-blitmask-wings-1.png'))
_player_wings_blitmask_2 = pygame.image.load(src.data.filepath('player-blitmask-wings-2.png'))
_player_wings_blitmask_3 = pygame.image.load(src.data.filepath('player-blitmask-wings-3.png'))
_player_polish = pygame.image.load(src.data.filepath('player-polish.png'))

import src.main
while True:
	difficulty = src.main.TitleScreen().run(screen)
	if difficulty is None:
		break
		
	player = src.sprite.Player((100, 316), (57, 82), (30, 46), (15, 29), (
	  src.textures.LYR_COTTON_TEX,
	  src.textures.LYR_FEATHER_TEX,
	 ),
	 (
	  (
		(-9, -43, _player_torso_blitmask),
		(-3, 0, _player_wings_blitmask_1),
	  ),
	  (
		(-9, -43, _player_torso_blitmask),
		(-4, -15, _player_wings_blitmask_2),
	  ),
	  (
		(-9, -43, _player_torso_blitmask),
		(0, -25, _player_wings_blitmask_3),
	  ),
	  (
		(-9, -43, _player_torso_blitmask),
		(-4, -15, _player_wings_blitmask_2),
	  ),
	 ),
	 _player_polish,
	 0, 5, 5, None, None, 1, 0
	)
	if difficulty == src.main.CASUAL:
		player.lives = 10
		
	pygame.mixer.music.play(-1)
	results = src.main.Game(difficulty).run(player, screen)
	pygame.mixer.music.fadeout(250)
	if results:
		if not src.main.Conclusion(results, player, difficulty).run(screen):
			break
	else:
		break
		
