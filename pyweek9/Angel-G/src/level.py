import locale
import pygame
import math

import data
import sprite
import textures
import main

_BULLET_STOCK = 16
_BULLET_COOLDOWN = 3
_BULLET_RELOAD = 12
_FEATHER_COOLDOWN = 10

_MOVEMENT = 8

class Level(object):
	_frame = 0
	_bullet_cooldown = 0
	_bullet_reload = 0
	_bullet_stock = _BULLET_STOCK
	_feather_cooldown = 0
	
	def __init__(self, descriptor, difficulty, player, background):
		pygame.display.set_caption("Angel-G - Level %i" % (int(descriptor)))
		
		self._events = []
		for line in open(data.filepath('script-level-%s.evt' % (descriptor))):
			line = line.strip()
			if line:
				if not line.startswith('#'):
					(index, event) = line.split(':', 1)
					self._events.append((int(index), event))
		self._events.sort()
		
		self._player = player
		self._difficulty = difficulty
		self._descriptor = descriptor
		
		self._font = pygame.font.Font(data.filepath('font-Windsong.ttf'), 30)
		self._pause_overlay = pygame.font.Font(data.filepath('font-Windsong.ttf'), 100).render("Paused", True, (0, 0, 0))
		self._font_small = pygame.font.Font(data.filepath('font-Windsong.ttf'), 20)
		self._level_surface = self._font.render("Level %i" % (int(descriptor)), True, (255, 255, 255))
		self._multiplier_overlay = pygame.image.load(data.filepath('icon-multiplier.png'))
		self._life = pygame.image.load(data.filepath('icon-life.png'))
		self._feather = pygame.image.load(data.filepath('icon-feather.png'))
		self._updateTarGunSurface()
		self._updateSupportSurface()
		self._updateScoreSurface()
		self._updateLivesSurface()
		self._updateFeathersSurface()
		self._updateMultiplierSurface()
		
		self._sound_gun_3_shot = pygame.mixer.Sound(data.filepath('sound-3-shot.ogg'))
		self._sound_gun_5_shot = pygame.mixer.Sound(data.filepath('sound-5-shot.ogg'))
		self._sound_gun_3_way = pygame.mixer.Sound(data.filepath('sound-3-way.ogg'))
		self._sound_gun_rapid = pygame.mixer.Sound(data.filepath('sound-rapid.ogg'))
		self._sound_gun_3_shot.set_volume(0.75)
		self._sound_gun_5_shot.set_volume(0.75)
		self._sound_gun_3_way.set_volume(0.75)
		self._sound_gun_rapid.set_volume(0.75)
		
		self._sound_spt_movement = pygame.mixer.Sound(data.filepath('sound-mobility.ogg'))
		self._sound_spt_reload = pygame.mixer.Sound(data.filepath('sound-reload.ogg'))
		self._sound_spt_shield = pygame.mixer.Sound(data.filepath('sound-shield.ogg'))
		self._sound_spt_tar = pygame.mixer.Sound(data.filepath('sound-tar.ogg'))
		self._sound_spt_movement.set_volume(0.75)
		self._sound_spt_reload.set_volume(0.75)
		self._sound_spt_shield.set_volume(0.75)
		self._sound_spt_tar.set_volume(0.75)
		
		self._sound_bns_feather = pygame.mixer.Sound(data.filepath('sound-feather.ogg'))
		self._sound_bns_life = pygame.mixer.Sound(data.filepath('sound-life.ogg'))
		self._sound_bns_feather.set_volume(0.75)
		self._sound_bns_life.set_volume(0.75)
		
		self._sound_bomb = pygame.mixer.Sound(data.filepath('sound-bomb.ogg'))
		self._sound_death = pygame.mixer.Sound(data.filepath('sound-death.ogg'))
		self._sound_bomb.set_volume(0.75)
		self._sound_death.set_volume(0.75)
		
		self._background = background
		
		self._obstacles = []
		self._obstacle_textures = (
		 textures.OBS_BRICK_TEX,
		 textures.OBS_CARPET_TEX,
 		 textures.OBS_DENIM_TEX,
		 textures.OBS_TWEED_TEX,
		)
		self._explosions = []
		self._explosion_blitmasks = (
		 pygame.image.load(data.filepath('explosion-blitmask-1.png')),
		 pygame.image.load(data.filepath('explosion-blitmask-2.png')),
		 pygame.image.load(data.filepath('explosion-blitmask-3.png')),
		 pygame.image.load(data.filepath('explosion-blitmask-4.png')),
		)
		
		self._bullets_fired = 0
		self._bullets_landed = 0
		
		self._bullets_player = []
		self._bullets_enemy = []
		
		self._zombies = []
		self._zombie_textures = (
		 textures.LYR_SLIME_1_TEX,
		 textures.LYR_SLIME_2_TEX,
		 textures.LYR_SLIME_3_TEX,
		)
		
		self._objects = []
		self._smoke = []
		self._zombie_smoke = (
		 pygame.image.load(data.filepath('zombie-smoke70.png')),
		 pygame.image.load(data.filepath('zombie-smoke40.png')),
		 pygame.image.load(data.filepath('zombie-smoke25.png')),
		)
		
		self._score = 0
		self._zombies_tarred = 0
		self._zombies_feathered = 0
		self._zombies_total = 0
		
		self._zombie_pool = (
		 (
		  sprite.Zombie_Straight_None,
		  sprite.Zombie_Straight_Horizontal,
		  sprite.Zombie_Straight_Horizontals,
		  sprite.Zombie_Straight_Vertical,
		  sprite.Zombie_Straight_Verticals,
		  sprite.Zombie_Straight_Cross,
		  sprite.Zombie_Straight_Angle30,
		  sprite.Zombie_Straight_Angle30s,
		  sprite.Zombie_Straight_Angle45,
		  sprite.Zombie_Straight_Angle45s,
		  sprite.Zombie_Straight_Angle60,
		  sprite.Zombie_Straight_Angle60s,
		  sprite.Zombie_Straight_Star,
		  sprite.Zombie_Straight_Target,
		  sprite.Zombie_Straight_TargetCross,
		  sprite.Zombie_Straight_TargetAngle45s,
		  sprite.Zombie_Straight_Horizontals_Verticals,
		  sprite.Zombie_Straight_Cross_Angle45s,
		  sprite.Zombie_Straight_Star_Target,
		  sprite.Zombie_Straight_Target_Cross,
		  sprite.Zombie_Straight_Target_Angle45s,
		 ),
		 (
		  sprite.Zombie_Shift_None,
		  sprite.Zombie_Shift_Horizontal,
		  sprite.Zombie_Shift_Horizontals,
		  sprite.Zombie_Shift_Vertical,
		  sprite.Zombie_Shift_Verticals,
		  sprite.Zombie_Shift_Cross,
		  sprite.Zombie_Shift_Angle30,
		  sprite.Zombie_Shift_Angle30s,
		  sprite.Zombie_Shift_Angle45,
		  sprite.Zombie_Shift_Angle45s,
		  sprite.Zombie_Shift_Angle60,
		  sprite.Zombie_Shift_Angle60s,
		  sprite.Zombie_Shift_Star,
		  sprite.Zombie_Shift_Target,
		  sprite.Zombie_Shift_TargetCross,
		  sprite.Zombie_Shift_TargetAngle45s,
		  sprite.Zombie_Shift_Horizontals_Verticals,
		  sprite.Zombie_Shift_Cross_Angle45s,
		  sprite.Zombie_Shift_Star_Target,
		  sprite.Zombie_Shift_Target_Cross,
		  sprite.Zombie_Shift_Target_Angle45s,
		 ),
		 (
		  sprite.Zombie_Swoop_None,
		  sprite.Zombie_Swoop_Horizontal,
		  sprite.Zombie_Swoop_Horizontals,
		  sprite.Zombie_Swoop_Vertical,
		  sprite.Zombie_Swoop_Verticals,
		  sprite.Zombie_Swoop_Cross,
		  sprite.Zombie_Swoop_Angle30,
		  sprite.Zombie_Swoop_Angle30s,
		  sprite.Zombie_Swoop_Angle45,
		  sprite.Zombie_Swoop_Angle45s,
		  sprite.Zombie_Swoop_Angle60,
		  sprite.Zombie_Swoop_Angle60s,
		  sprite.Zombie_Swoop_Star,
		  sprite.Zombie_Swoop_Target,
		  sprite.Zombie_Swoop_TargetCross,
		  sprite.Zombie_Swoop_TargetAngle45s,
		  sprite.Zombie_Swoop_Horizontals_Verticals,
		  sprite.Zombie_Swoop_Cross_Angle45s,
		  sprite.Zombie_Swoop_Star_Target,
		  sprite.Zombie_Swoop_Target_Cross,
		  sprite.Zombie_Swoop_Target_Angle45s,
		 ),
		)
		
		self._field = pygame.Rect((0, 50), (800, 550))
		
	def run(self, _screen, _keys):
		_clock = pygame.time.Clock()
		_paused = False
		while True:
			for e in pygame.event.get():
				if e.type == pygame.KEYDOWN:
					_keys.add(e.key)
					if e.key == pygame.K_TAB:
						_paused = not _paused
						if _paused:
							pygame.mixer.music.pause()
							_screen.blit(self._pause_overlay, ((800 - self._pause_overlay.get_width()) / 2, 50 + (550 - self._pause_overlay.get_height()) / 2))
							pygame.display.flip()
						else:
							pygame.mixer.music.unpause()
							
				elif e.type == pygame.KEYUP:
					_keys.discard(e.key)
				elif e.type == pygame.QUIT:
					return None
					
			_clock.tick(20)
			if _paused:
				continue
				
			(complete, action, feathered_zombies) = self._tick(_keys)
			if complete:
				return (self._score, self._zombies_tarred, self._zombies_feathered, self._zombies_total, self._bullets_fired, self._bullets_landed, self._descriptor)
				
			#Prepare for next frame.
			_screen.blit(self._background, (0, 50))
			
			#Render obstacles.
			for obstacle in self._obstacles:
				obstacle.render(_screen, self._field)
				
			#Render the player.
			self._player.render(_screen, action)
			
			#Render smoke.
			for (frame, (x, y)) in self._smoke:
				_screen.blit(self._zombie_smoke[frame], (x - 8, y - 8))
				
			#Render zombies.
			for zombie in self._zombies:
				zombie.render(_screen)
				
			#Render bullets.
			for bullet in self._bullets_player:
				bullet.render(_screen)
			for bullet in self._bullets_enemy:
				bullet.render(_screen)
				
			#Render objects.
			for obj in self._objects:
				obj.render(_screen)
				
			#Render explosions.
			for (frame, change_next, position) in self._explosions:
				sprite.render(textures.LYR_EXPLOSION_TEX, self._explosion_blitmasks[frame], position, _screen)
				
			#Render stats.
			self._renderStats(_screen)
			
			if not feathered_zombies is None: #Render the feather-bomb effect, if appropriate.
				player_position = self._player.getPosition()
				screen_backup = _screen.copy()
				self._sound_bomb.play()
				sprite.render(textures.LYR_FEATHER_TEX, sprite.FTH_EPICENTRE_1, player_position, _screen)
				pygame.display.flip()
				_clock.tick(20)
				
				_screen.blit(screen_backup, (0, 50), (0, 50, 800, 550))
				sprite.render(textures.LYR_FEATHER_TEX, sprite.FTH_EPICENTRE_2, player_position, _screen)
				pygame.display.flip()
				_clock.tick(20)
				
				for zombie in [z for z in feathered_zombies]:
					sprite.render(textures.LYR_FEATHER_TEX, sprite.FTH_APPLY, zombie.getPosition(), screen_backup)
				_screen.blit(screen_backup, (0, 50), (0, 50, 800, 550))
				pygame.display.flip()
				
				#Roll the feathers across the screen.
				for i in xrange(14):
					offset = (i - 3) * 80
					_screen.blit(textures.LYR_FEATHER_TEX, (offset, 50), (offset, 0, 320, 550))
					_screen.blit(screen_backup, (offset - 80, 50), (offset - 80, 50, 80, 550))
					
					sprite.render(textures.LYR_FEATHER_TEX, sprite.FTH_EPICENTRE_3, player_position, _screen)
					
					pygame.display.flip()
					_clock.tick(20)
					
				_screen.blit(screen_backup, (0, 50), (0, 50, 800, 550))
				pygame.display.flip()
				
				_clock.tick(4)
				del screen_backup
				
				
				live_bullets = []
				(p_x, p_y) = player_position
				for bullet in self._bullets_enemy:
					(b_x, b_y) = bullet.center
					if math.sqrt((p_x - b_x) ** 2 + (p_y - b_y) ** 2) > 75.0:
						live_bullets.append(bullet)
				self._bullets_enemy = live_bullets
			else:	#Display the new frame.
				pygame.display.flip()
				
	def _clearOffscreen(self, rects):
		for rect in rects:
			rect.tick()
		live_rects = self._field.collidelistall(rects)
		for i in range(len(rects) - 1, -1, -1):
			if not i in live_rects:
				del rects[i]
				
	def _tick(self, keys):
		action = None
		feathered_zombies = None
		feather_bomb = False
		(update_multiplier,) = self._player.tick()
		update_score = False
		update_lives = False
		
		#Update explosions.
		dead_explosions = []
		for (i, explosion) in enumerate(self._explosions):
			if explosion[1]:
				if explosion[0] == 3:
					dead_explosions.append(explosion)
				else:
					explosion[0] += 1
					explosion[1] = False
			else:
				explosion[1] = True
		for explosion in dead_explosions:
			self._explosions.remove(explosion)
			
		#Update smoke.
		dead_smoke = []
		for (i, smoke) in enumerate(self._smoke):
			smoke[0] += 1
			if smoke[0] == 3:
				dead_smoke.append(i)
			else:
				(x, y) = smoke[1]
				smoke[1] = (x + 3, y)
		for i in reversed(dead_smoke):
			del self._smoke[i]
			
		#Update zombies.
		dead_zombies = []
		for (i, zombie) in enumerate(self._zombies):
			trail_position = zombie.getTrailPosition()
			self._bullets_enemy += zombie.tick(self._player)
			if not self._field.colliderect(zombie.getHitbox()):
				dead_zombies.append(i)
			elif zombie.state == sprite.ZMB_NORMAL:
				self._smoke.append([0, (trail_position)])
		for i in reversed(dead_zombies):
			del self._zombies[i]
			
		#Update obstacles and bullets and objects.
		self._clearOffscreen(self._obstacles)
		self._clearOffscreen(self._bullets_player)
		self._clearOffscreen(self._bullets_enemy)
		self._clearOffscreen(self._objects)
		
		#Update player position.
		offset_x = 0
		offset_y = 0
		if pygame.K_UP in keys:
			offset_y -= _MOVEMENT
		if pygame.K_DOWN in keys:
			offset_y += _MOVEMENT
		if pygame.K_LEFT in keys:
			offset_x -= _MOVEMENT
		if pygame.K_RIGHT in keys:
			offset_x += _MOVEMENT
		if offset_x or offset_y:
			if pygame.K_LSHIFT in keys:
				boost = 2
				if self._player.support == sprite.SPT_MOVEMENT:
					boost = 3
				offset_x *= boost
				offset_y *= boost
			self._player.setPositionRelative(offset_x, offset_y)
			if offset_y > 0:
				action = sprite.ACT_DIVE
			elif offset_y < 0:
				action = sprite.ACT_SOAR
			else:
				action = sprite.ACT_NONE
				
		#Process player actions.
		if self._feather_cooldown:
			self._feather_cooldown -= 1
		else:
			if pygame.K_LCTRL in keys and self._player.feathers:
				self._player.feathers -= 1
				self._feather_cooldown = _FEATHER_COOLDOWN
				feather_bomb = True
				self._updateFeathersSurface()
				
		if self._bullet_cooldown:
			self._bullet_cooldown = max(0, self._bullet_cooldown - 1)
		elif self._bullet_reload:
			self._bullet_reload = max(0, self._bullet_reload - 1)
			if not self._bullet_reload:
				self._bullet_stock = _BULLET_STOCK
		elif pygame.K_SPACE in keys:
			self._bullets_fired += 1
			
			(x, y) = self._player.getHitbox().center
			self._bullets_player.append(sprite.TarBullet((x + 23, y + 6), (20, 0)))
			gun_type = self._player.tar_gun
			if gun_type == sprite.GUN_3_SHOT:
				new_bullet = sprite.TarBullet((x + 23, y - 40), (20, 0))
				new_bullet.hide(1)
				self._bullets_player.append(new_bullet)
				new_bullet = sprite.TarBullet((x + 23, y + 52), (20, 0))
				new_bullet.hide(1)
				self._bullets_player.append(new_bullet)
			elif gun_type == sprite.GUN_5_SHOT:
				self._bullet_cooldown += (_BULLET_COOLDOWN * 3) / 2
				
				new_bullet = sprite.TarBullet((x + 23, y - 7), (20, 0))
				new_bullet.hide(1)
				self._bullets_player.append(new_bullet)
				new_bullet = sprite.TarBullet((x + 23, y + 19), (20, 0))
				new_bullet.hide(1)
				self._bullets_player.append(new_bullet)
				
				new_bullet = sprite.TarBullet((x + 23, y - 23), (20, 0))
				new_bullet.hide(2)
				self._bullets_player.append(new_bullet)
				new_bullet = sprite.TarBullet((x + 23, y + 35), (20, 0))
				new_bullet.hide(2)
				self._bullets_player.append(new_bullet)
			elif gun_type == sprite.GUN_3_WAY:
				self._bullet_cooldown += _BULLET_COOLDOWN / 2
				
				new_bullet = sprite.TarBullet((x + 23, y + 6), (20, 5))
				new_bullet.hide(1)
				self._bullets_player.append(new_bullet)
				new_bullet = sprite.TarBullet((x + 23, y + 6), (20, -5))
				new_bullet.hide(1)
				self._bullets_player.append(new_bullet)
				
			if gun_type == sprite.GUN_RAPID:
				self._bullet_cooldown += _BULLET_COOLDOWN / 2
				self._bullet_stock -= 1
			else:
				self._bullet_cooldown += _BULLET_COOLDOWN
				self._bullet_stock -= 2
			if self._bullet_stock <= 0:
				if self._player.support == sprite.SPT_RELOAD:
					self._bullet_reload = _BULLET_RELOAD / 2
				else:
					self._bullet_reload = _BULLET_RELOAD
		else:
			self._bullet_stock = min(_BULLET_STOCK, self._bullet_stock + 1)
			
		#Process pending events.
		while self._events:
			if self._events[0][0] == self._frame:
				event = self._events.pop(0)[1].split(':')
				if event[0] == 'zmb':
					self._zombies_total += 1
					
					zombie_level = int(event[1])
					zombie = self._zombie_pool[int(event[2])][int(event[3])](
					 self._difficulty, zombie_level + 1, event[4], event[5], event[6],
					 (825, int(event[7]) + 50),
					 (52, 61), (46, 56), (3, 3), (
					  self._zombie_textures[zombie_level],
					  textures.LYR_METAL_TEX,
					 ),
					 (
					  (
					   (0, 0, sprite.ZMB_BLITMASK_BODY),
					   (-22, -13, sprite.ZMB_BLITMASK_JETPACK),
					  ),
					 ),
					 sprite.ZMB_POLISH_TEX
					)
					
					if len(event) == 10:
						zombie.setItem(self._parseObject(event[8], event[9], (0, 0)))
						
					self._zombies.append(zombie)
				elif event[0] == 'obs':
					dimensions = map(int, event[2].split(','))
					velocity = (-7, 0)
					offset = int(event[3])
					position = None
					if len(event) == 6:
						velocity = map(int, event[5].split(','))
						if event[4] == 'top':
							position = (offset - dimensions[0] / 2, 50 - dimensions[1])
						elif event[4] == 'bottom':
							position = (offset - dimensions[0] / 2, 549)
						elif event[4] == 'left':
							position = (-dimensions[0], offset + 50 - dimensions[1] / 2)
						else:
							position = (799, offset + 50 - dimensions[1] / 2)
					else:
						position = (799, offset + 50 - dimensions[1] / 2)
						
					self._obstacles.append(
					 sprite.Obstacle(
					  position,
					  dimensions,
					  velocity,
					  self._obstacle_textures[int(event[1])]
					 )
					)
				elif event[0] == 'obj':
					x = 815
					y = int(event[3]) + 50
					self._objects.append(self._parseObject(event[1], event[2], (x, y)))
				elif event[0] == 'win':
					return (True, action, feathered_zombies)
			else:
				break
		self._frame += 1
		
		#Detect collisions.
		if self._player.isVulnerable() or not self._difficulty == main.DIFFICULT:
			for obj in reversed(self._objects):
				if self._player.getHitbox().colliderect(obj):
					result = obj.trigger(self._player)
					if result == sprite.OBJ_LIFE:
						self._sound_bns_life.play()
						update_lives = True
					elif result == sprite.OBJ_FEATHER:
						self._sound_bns_feather.play()
						self._updateFeathersSurface()
					elif result == sprite.OBJ_SUPPORT:
						if self._player.support == sprite.SPT_TAR: self._sound_spt_tar.play()
						elif self._player.support == sprite.SPT_SHIELD: self._sound_spt_shield.play()
						elif self._player.support == sprite.SPT_RELOAD: self._sound_spt_reload.play()
						elif self._player.support == sprite.SPT_MOVEMENT: self._sound_spt_movement.play()
						self._updateSupportSurface()
					elif result == sprite.OBJ_POWERUP:
						if self._player.tar_gun == sprite.GUN_3_SHOT: self._sound_gun_3_shot.play()
						elif self._player.tar_gun == sprite.GUN_5_SHOT: self._sound_gun_5_shot.play()
						elif self._player.tar_gun == sprite.GUN_3_WAY: self._sound_gun_3_way.play()
						elif self._player.tar_gun == sprite.GUN_RAPID: self._sound_gun_rapid.play()
						self._updateTarGunSurface()
					self._objects.remove(obj)
					
		if self._player.isVulnerable():
			player_hitbox = self._player.getHitbox()
			if player_hitbox.collidelistall(self._obstacles):
				if not self._player.kill():
					return (True, action, feathered_zombies)
				self._sound_death.play()
				update_lives = True
				self._updateTarGunSurface()
				self._updateSupportSurface()
				self._explosions.append([0, False, player_hitbox.center])
				
			if player_hitbox.collidelistall(self._bullets_enemy):
				if self._player.support == sprite.SPT_SHIELD:
					self._player.nick()
				else:
					if not self._player.kill():
						return (True, action, feathered_zombies)
					self._sound_death.play()
					update_lives = True
					self._updateTarGunSurface()
				self._updateSupportSurface()
				self._explosions.append([0, False, player_hitbox.center])
				
			if player_hitbox.collidelistall([zombie.getHitbox() for zombie in self._zombies if zombie.state == sprite.ZMB_NORMAL]):
				if not self._player.kill():
						return (True, None)
				self._sound_death.play()
				update_lives = True
				self._updateTarGunSurface()
				self._updateSupportSurface()
				self._explosions.append([0, False, player_hitbox.center])
				
		dead_bullets = set()
		dead_zombies = []
		for zombie in self._zombies:
			zombie_hitbox = zombie.getHitbox()
			if zombie.state == sprite.ZMB_NORMAL:
				landed_bullets = zombie_hitbox.collidelistall(self._bullets_player)
				if landed_bullets:
					for i in xrange(len(landed_bullets)):
						if zombie.tar():
							new_points = 2000 * self._player.multiplier * zombie.level
							update_lives = self._player.addScore(new_points) or update_lives
							self._score += new_points
							if zombie.state == sprite.ZMB_TARRED:
								self._zombies_tarred += 1
								item = zombie.getItem()
								if item:
									self._objects.append(item)
						else:
							new_points = 500 * self._player.multiplier * zombie.level
							update_lives = self._player.addScore(new_points) or update_lives
							self._score += new_points
					update_score = True
					if self._player.multiplier > 1:
						self._player.multiplier_cooldown = 60
					self._bullets_landed += len(landed_bullets)
					dead_bullets.update(set(landed_bullets))
					
			if zombie_hitbox.collidelistall(self._obstacles):
				self._explosions.append([0, False, zombie_hitbox.center])
				dead_zombies.append(zombie)
		for i in reversed(sorted(dead_bullets)):
			del self._bullets_player[i]
		for zombie in dead_zombies:
			self._zombies.remove(zombie)
			
		self._clearDeadBullets(self._bullets_player)
		self._clearDeadBullets(self._bullets_enemy)
		
		if feather_bomb:
			ignore_tarred = self._player.support == sprite.SPT_TAR
			feathered_zombies = []
			tarred_zombies = 0
			for zombie in self._zombies:
				zombie_normal = zombie.state == sprite.ZMB_NORMAL
				if zombie.feather(ignore_tarred):
					feathered_zombies.append(zombie)
					if zombie_normal:
						tarred_zombies += 1
						item = zombie.getItem()
						if item:
							self._objects.append(item)
			feathered_zombie_count = len(feathered_zombies)
			new_points = 10000 * feathered_zombie_count * self._player.multiplier * zombie.level
			update_lives = self._player.addScore(new_points) or update_lives
			self._score += new_points
			if feathered_zombie_count:
				self._player.multiplier_cooldown = 60
				self._player.multiplier += feathered_zombie_count
				self._zombies_feathered += feathered_zombie_count
			update_score = True
			update_multiplier = True
			
		#Update the player's stats.
		if update_multiplier:
			self._updateMultiplierSurface()
		if update_score:
			self._updateScoreSurface()
		if update_lives:
			self._updateLivesSurface()
			
		return (False, action, feathered_zombies)
		
	def _clearDeadBullets(self, bullet_list):
		dead_bullets = set()
		for obstacle in self._obstacles:
			dead_bullets.update(set(obstacle.collidelistall(bullet_list)))
		for i in reversed(sorted(dead_bullets)):
			del bullet_list[i]
			
	def _parseObject(self, category, type, position):
		if category == 'spt':
			obj_type = None
			if type == 'tar':
				obj_type = sprite.SPT_TAR
			elif type == 'shield':
				obj_type = sprite.SPT_SHIELD
			elif type == 'reload':
				obj_type = sprite.SPT_RELOAD
			elif type == 'movement':
				obj_type = sprite.SPT_MOVEMENT
			return sprite.Support(position, obj_type)
		elif category == 'gun':
			obj_type = None
			if type == '3-shot':
				obj_type = sprite.GUN_3_SHOT
			elif type == '5-shot':
				obj_type = sprite.GUN_5_SHOT
			elif type == '3-way':
				obj_type = sprite.GUN_3_WAY
			elif type == 'rapid':
				obj_type = sprite.GUN_RAPID
			return sprite.Powerup(position, obj_type)
		elif category == 'bns':
			if type == 'life':
				return sprite.BonusLife(position)
			elif type == 'feather':
				return sprite.BonusFeather(position)
				
	def _renderStats(self, screen):
		screen.fill((0, 0, 0), (0, 0, 800, 50))
		pygame.draw.line(screen, (255, 255, 255), (0, 50), (799, 50))
		
		screen.blit(self._score_surface, (4, -1))
		screen.blit(self._multiplier_surface, (0, 25))
		if self._player.multiplier_cooldown:
			screen.fill((220, 220, 220), (0, 36, 207 * (self._player.multiplier_cooldown / 60.0), 3))
		screen.blit(self._lives_surface, (275, 0))
		screen.blit(self._feathers_surface, (275, 25))
		screen.blit(self._support_surface, (575, -1))
		screen.blit(self._level_surface, (797 - self._level_surface.get_width(), -1))
		screen.blit(self._tar_gun_surface, (797 - self._tar_gun_surface.get_width(), 24))
		
	def _updateTarGunSurface(self):
		text = "Basic Burst"
		if self._player.tar_gun == sprite.GUN_3_SHOT:
			text = "Three-shot Burst"
		elif self._player.tar_gun == sprite.GUN_5_SHOT:
			text = "Five-shot Burst"
		elif self._player.tar_gun == sprite.GUN_3_WAY:
			text = "Three-way Fork"
		elif self._player.tar_gun == sprite.GUN_RAPID:
			text = "Rapid-fire Stream"
		self._tar_gun_surface = self._font.render(text, True, (255, 255, 255))
		
	def _updateSupportSurface(self):
		text = "No Support"
		if self._player.support == sprite.SPT_TAR:
			text = "Automatic Tarring"
		elif self._player.support == sprite.SPT_SHIELD:
			text = "Anti-bullet Shield"
		elif self._player.support == sprite.SPT_RELOAD:
			text = "Double-speed Reload"
		elif self._player.support == sprite.SPT_MOVEMENT:
			text = "Enhanced Mobility"
		self._support_surface = self._font.render(text, True, (255, 255, 255))
		
	def _updateScoreSurface(self):
		self._score_surface = self._font.render(locale.format("%d", self._player.score, 1), True, (255, 255, 255))
		
	def _updateLivesSurface(self):
		self._lives_surface = pygame.Surface((max(self._player.lives * self._life.get_width() + self._player.lives - 1, 0), 25))
		offset = 0
		for life in xrange(self._player.lives):
			self._lives_surface.blit(self._life, (offset, 2))
			offset += self._life.get_width() + 1
			
	def _updateFeathersSurface(self):
		self._feathers_surface = pygame.Surface((max(self._player.feathers * self._feather.get_width() + self._player.feathers - 1, 0), 25))
		offset = 0
		for feather in xrange(self._player.feathers):
			self._feathers_surface.blit(self._feather, (offset, 2))
			offset += self._feather.get_width() + 1
			
	def _updateMultiplierSurface(self):
		self._multiplier_surface = self._multiplier_overlay.copy()
		multiplier_value = self._font_small.render(str(self._player.multiplier), True, (255, 255, 255))
		self._multiplier_surface.blit(multiplier_value, (252 - multiplier_value.get_width(), 1))
		
