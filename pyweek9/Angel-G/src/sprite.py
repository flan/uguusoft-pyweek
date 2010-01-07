import random
import pygame

import main
import data
import textures

ACT_NONE = 0
ACT_SOAR = 1
ACT_DIVE = 2

GUN_BASE = 0
GUN_3_SHOT = 1
GUN_5_SHOT = 2
GUN_3_WAY = 3
GUN_RAPID = 4

SPT_NONE = 0
SPT_TAR = 1
SPT_SHIELD = 2
SPT_RELOAD = 3
SPT_MOVEMENT = 4

OBJ_LIFE = 0
OBJ_FEATHER = 1
OBJ_SUPPORT = 2
OBJ_POWERUP = 3

ZMB_NORMAL = 0
ZMB_TARRED = 1
ZMB_FEATHERED = 2

_GUN_3_SHOT_TEX = pygame.image.load(data.filepath('powerup-3-shot.png'))
_GUN_5_SHOT_TEX = pygame.image.load(data.filepath('powerup-5-shot.png'))
_GUN_3_WAY_TEX = pygame.image.load(data.filepath('powerup-3-way.png'))
_GUN_RAPID_TEX = pygame.image.load(data.filepath('powerup-rapid.png'))

_SPT_TAR_TEX = pygame.image.load(data.filepath('support-auto-tar.png'))
_SPT_SHIELD_TEX = pygame.image.load(data.filepath('support-bullet-shield.png'))
_SPT_RELOAD_TEX = pygame.image.load(data.filepath('support-half-reload.png'))
_SPT_MOVEMENT_TEX = pygame.image.load(data.filepath('support-triple-movement.png'))

_BNS_FEATHER_TEX = pygame.image.load(data.filepath('bonus-feather.png'))
_BNS_LIFE_TEX = pygame.image.load(data.filepath('bonus-life.png'))

ZMB_BLITMASK_BODY = pygame.image.load(data.filepath('zombie-blitmask-body.png'))
ZMB_BLITMASK_JETPACK = pygame.image.load(data.filepath('zombie-blitmask-jetpack.png'))
ZMB_POLISH_TEX = pygame.image.load(data.filepath('zombie-polish.png'))

FTH_EPICENTRE_1 = pygame.image.load(data.filepath('feather-epicentre-1.png'))
FTH_EPICENTRE_2 = pygame.image.load(data.filepath('feather-epicentre-2.png'))
FTH_EPICENTRE_3 = pygame.image.load(data.filepath('feather-epicentre-3.png'))
FTH_APPLY = pygame.image.load(data.filepath('feather-apply.png'))

class _Sprite(object):
	_frame = 0
	_frame_swap = 0
	
	def __init__(self, position, dimensions, hitbox_dimensions, hitbox_centre, textures, blitmasks_data, polish_texture):
		self._textures = textures
		self._frames = tuple([_Frame(blitmasks) for blitmasks in blitmasks_data])
		self._polish_texture = polish_texture
		(self._centre_w, self._centre_v) = [n / 2 for n in dimensions]
		(self._hb_centre_w, self._hb_centre_v) = hitbox_dimensions
		(self._hb_centre_x, self._hb_centre_y) = hitbox_centre
		self.setPosition(position)
		
	def getHitbox(self):
		return self._hitbox
		
	def getPosition(self):
		return self._position
		
	def setPosition(self, position):
		self._position = (x, y) = position
		self._hitbox = pygame.Rect((x - self._centre_w + self._hb_centre_x, y - self._centre_v + self._hb_centre_y), (self._hb_centre_w, self._hb_centre_v))
		
	def setPositionRelative(self, x, y):
		(x_pos, y_pos) = self._position
		self.setPosition((x_pos + x, y_pos + y))
		
	def _render(self, screen):
		self._frames[self._frame].render(self._textures, self._position, self._centre_w, self._centre_v, screen)
		self._frame_swap += 1
		if self._frame_swap >= 4:
			self._frame += 1
			if self._frame == len(self._frames):
				self._frame = 0
			self._frame_swap = 0
			
	def renderPolish(self, screen):
		screen.blit(self._polish_texture, (self._position[0] - self._centre_w, self._position[1] - self._centre_v))
		
		
class _Frame(object):
	def __init__(self, blitmasks):
		self._blitmasks = blitmasks
		
	def render(self, textures, position, centre_w, centre_v, screen):
		(pos_x, pos_y) = position
		for ((x, y, blitmask), texture) in zip(self._blitmasks, textures):
			left = pos_x - x - centre_w
			top = pos_y - y - centre_v
			(width, height) = blitmask.get_size()
			
			working_surface = pygame.Surface((width, height), flags=(pygame.constants.SRCALPHA | pygame.constants.SWSURFACE))
			working_surface.blit(texture, (0, 0), ((left, top - 50), (width, height)))
			working_surface.blit(blitmask, (0, 0), None, pygame.constants.BLEND_RGBA_SUB)
			
			screen.blit(working_surface, (left, top))
			
			
class _Zombie(_Sprite):
	state = ZMB_NORMAL
	_offset = 0
	_velocity_x = 7
	_velocity_y = 0
	_life_frame = 0
	_item = None
	_origin_y = None
	_boundary_y = None
	_event_1 = None
	_event_2 = None
	_initial_x = None
	
	def __init__(self, difficulty, level, speed, event_1, event_2, position, dimensions, hitbox_dimensions, hitbox_centre, textures, blitmasks_data, polish_texture):
		_Sprite.__init__(self, position, dimensions, hitbox_dimensions, hitbox_centre, textures, blitmasks_data, polish_texture)
		self._bullet_cooldown = 18
		if difficulty == main.CASUAL:
			self._bullet_cooldown = 26
		elif difficulty == main.DIFFICULT:
			self._bullet_cooldown = 14
		self._hp = self.level = level
		self._origin_y = position[1] - 50
		if event_1:
			self._event_1 = int(event_1)
		if event_2:
			self._event_2 = int(event_2)
		if speed:
			self._velocity_x = int(speed)
		self._initial_x = self._velocity_x
		
	def setItem(self, item):
		self._item = item
		
	def getItem(self):
		if self._item:
			self._item.center = self._position
		return self._item
		
	def getTrailPosition(self):
		offset = 0
		if self.state == ZMB_NORMAL:
			offset = random.randint(-1, 1)
			if offset < 0:
				self._offset = max(-5, self._offset + offset)
			elif offset > 0:
				self._offset = min(5, self._offset + offset)
		(x, y) = self._position
		return (x + 25, y + self._offset + 7)
		
	def render(self, screen):
		position = (x, y) = self._position
		self._position = (x, y + self._offset)
		self._frames[self._frame].render(self._textures, self._position, self._centre_w, self._centre_v, screen)
		if self.state == ZMB_NORMAL:
			self.renderPolish(screen)
		self._position = position
		
	def tar(self):
		if self._hp and self.state == ZMB_NORMAL:
			self._hp -= 1
			if not self._hp:
				self.state = ZMB_TARRED
				self._textures = (
				 textures.LYR_TAR_TEX,
				 textures.LYR_METAL_TEX,
				)
				return True
		return False
		
	def feather(self, ignore_tarred):
		if (ignore_tarred and self.state == ZMB_NORMAL) or self.state == ZMB_TARRED:
			self.state = ZMB_FEATHERED
			self._textures = (
			 textures.LYR_FEATHER_TEX,
			 textures.LYR_METAL_TEX,
			)
			return True
		return False
		
	def tick(self, player):
		bullets = None
		if self.state == ZMB_NORMAL:
			self._move()
			if self._life_frame % self._bullet_cooldown == 1:
				bullets = self._shoot(player)
			else:
				bullets = []
			self._life_frame += 1
		else:
			bullets = []
		self.setPositionRelative(-self._velocity_x, -self._velocity_y)
		return bullets
		
	def _getBulletOrigin(self):
		(x, y) = self._position
		x -= 15
		y += self._offset
		return (x, y)
		
	def _getHorizontalBullet(self, player):
		if self._position[0] > player.getHitbox().centerx:
			return [Bullet(self._getBulletOrigin(), (-10, 0))]
		else:
			return [Bullet(self._getBulletOrigin(), (10, 0))]
			
	def _getHorizontalBullets(self):
		return [
		 Bullet(self._getBulletOrigin(), (-10, 0)),
		 Bullet(self._getBulletOrigin(), (10, 0)),
		]
		
	def _getVerticalBullet(self, player):
		if self._position[1] < player.getHitbox().centery:
			return [Bullet(self._getBulletOrigin(), (0, 10))]
		elif self._position[1] > player.getHitbox().centery:
			return [Bullet(self._getBulletOrigin(), (0, -10))]
		return [Bullet(self._getBulletOrigin(), (0, random.choice((10, -10))))]
		
	def _getVerticalBullets(self):
		return [
		 Bullet(self._getBulletOrigin(), (0, 10)),
		 Bullet(self._getBulletOrigin(), (0, -10)),
		]
		
	def _get30AngleBullet(self, player):
		x = 8
		if self._position[0] > player.getHitbox().centerx:
			x = -8
		if self._position[1] < player.getHitbox().centery:
			return [Bullet(self._getBulletOrigin(), (x, 4))]
		elif self._position[1] > player.getHitbox().centery:
			return [Bullet(self._getBulletOrigin(), (x, -4))]
		return [Bullet(self._getBulletOrigin(), (x, random.choice((-4, 4))))]
		
	def _get30AngleBullets(self):
		bullet_origin = self._getBulletOrigin()
		return [
		 Bullet(bullet_origin, (8, 4)),
		 Bullet(bullet_origin, (8, -4)),
		 Bullet(bullet_origin, (-8, 4)),
		 Bullet(bullet_origin, (-8, -4)),
		]
		
	def _get45AngleBullet(self, player):
		x = 8
		if self._position[0] > player.getHitbox().centerx:
			x = -8
		if self._position[1] < player.getHitbox().centery:
			return [Bullet(self._getBulletOrigin(), (x, 8))]
		elif self._position[1] > player.getHitbox().centery:
			return [Bullet(self._getBulletOrigin(), (x, -8))]
		return [Bullet(self._getBulletOrigin(), (x, random.choice((-8, 8))))]
		
	def _get45AngleBullets(self):
		bullet_origin = self._getBulletOrigin()
		return [
		 Bullet(bullet_origin, (8, 8)),
		 Bullet(bullet_origin, (8, -8)),
		 Bullet(bullet_origin, (-8, 8)),
		 Bullet(bullet_origin, (-8, -8)),
		]
		
	def _get60AngleBullet(self, player):
		x = 4
		if self._position[0] > player.getHitbox().centerx:
			x = -4
		if self._position[1] < player.getHitbox().centery:
			return [Bullet(self._getBulletOrigin(), (x, 10))]
		elif self._position[1] > player.getHitbox().centery:
			return [Bullet(self._getBulletOrigin(), (x, -10))]
		return [Bullet(self._getBulletOrigin(), (x, random.choice((-10, 10))))]
		
	def _get60AngleBullets(self):
		bullet_origin = self._getBulletOrigin()
		return [
		 Bullet(bullet_origin, (4, 10)),
		 Bullet(bullet_origin, (4, -10)),
		 Bullet(bullet_origin, (-4, 10)),
		 Bullet(bullet_origin, (-4, -10)),
		]
		
	def _getTargetBullet(self, player):
		(p_x, p_y) = player.getHitbox().center
		(z_x, z_y) = origin = self._getBulletOrigin()
		x = p_x - z_x
		y = p_y - z_y
		ratio = 1.0
		if y: #Avoid division-by-zero.
			ratio = abs(x / float(y))
		apply_x = ratio * cmp(x, 0)
		apply_y = float(cmp(y, 0))
		x = y = 0.0
		while True:
			x += apply_x
			y += apply_y
			if abs(x) + abs(y) >= 14.0:
				break
		x = int(x)
		if x > 10:
			x = 10
		elif x < -10:
			x = -10
		if y > 10:
			y = 10
		elif y < -10:
			y = -10
		return [Bullet(origin, (x, y))]
		
class _Zombie_Straight(_Zombie):
	def _move(self):
		if self._life_frame == self._event_1:
			self._velocity_x = 0
		elif self._life_frame == self._event_2:
			self._velocity_x = self._initial_x
			
class _Zombie_Shift(_Zombie):
	def _move(self):
		#Compensates for half-sprite-height:30 and 50px screen offset.
		if self._event_1 <= self._life_frame < self._event_1 + 92:
			self._velocity_y = -(570 - self._origin_y - self._position[1]) / 26
		else:
			self._velocity_y = 0
			
class _Zombie_Swoop(_Zombie):
	def _move(self):
		#Compensates for half-sprite-height:30 and 50px screen offset.
		if self._event_1 <= self._life_frame < self._event_1 + 61:
			self._velocity_y = -(570 - self._origin_y - self._position[1]) / 15
		elif self._event_2 <= self._life_frame < self._event_2 + 61:
			self._velocity_y = -(20 + self._origin_y - self._position[1]) / 15
		else:
			self._velocity_y = 0
			
			
class _Zombie_OneShot(object):
	def _shoot(self, player):
		return self._shoot_(player)
		
class _Zombie_TwoShot(object):
	_alternate = False
	
	def _shoot(self, player):
		self._alternate = not self._alternate
		if self._alternate:
			return self._shoot__(player)
		else:
			return self._shoot_(player)
			
class _Zombie__None(object):
	def _shoot_(self, player):
		return []
		
class _Zombie__Vertical(object):
	def _shoot_(self, player):
		return self._getVerticalBullet(player)
		
class _Zombie__Verticals(object):
	def _shoot_(self, player):
		return self._getVerticalBullets()
		
class _Zombie__Horizontal(object):
	def _shoot_(self, player):
		return self._getHorizontalBullet(player)
		
class _Zombie__Horizontals(object):
	def _shoot_(self, player):
		return self._getHorizontalBullets()
		
class _Zombie__Cross(object):
	def _shoot_(self, player):
		return self._getHorizontalBullets() + self._getVerticalBullets()
		
class _Zombie__Angle30(object):
	def _shoot_(self, player):
		return self._get30AngleBullet(player)
		
class _Zombie__Angle30s(object):
	def _shoot_(self, player):
		return self._get30AngleBullets()
		
class _Zombie__Angle45(object):
	def _shoot_(self, player):
		return self._get45AngleBullet(player)
		
class _Zombie__Angle45s(object):
	def _shoot_(self, player):
		return self._get45AngleBullets()
		
class _Zombie__Angle60(object):
	def _shoot_(self, player):
		return self._get60AngleBullet(player)
		
class _Zombie__Angle60s(object):
	def _shoot_(self, player):
		return self._get60AngleBullets()
		
class _Zombie__Target(object):
	def _shoot_(self, player):
		return self._getTargetBullet(player)
		
class _Zombie__TargetCross(object):
	def _shoot_(self, player):
		return self._getTargetBullet(player) + self._getHorizontalBullets() + self._getVerticalBullets()
		
class _Zombie__TargetAngle45s(object):
	def _shoot_(self, player):
		return self._getTargetBullet(player) + self._get45AngleBullets()
		
class _Zombie__Star(object):
	def _shoot_(self, player):
		return self._getHorizontalBullets() + self._getVerticalBullets() + self._get45AngleBullets()
		
class _Zombie___Target(object):
	def _shoot__(self, player):
		return self._getTargetBullet(player)
		
class _Zombie___Verticals(object):
	def _shoot__(self, player):
		return self._getVerticalBullets()
		
class _Zombie___Cross(object):
	def _shoot__(self, player):
		return self._getHorizontalBullets() + self._getVerticalBullets()
		
class _Zombie___Angle45s(object):
	def _shoot__(self, player):
		return self._get45AngleBullets()
		
class Zombie_Straight_None(_Zombie_Straight, _Zombie_OneShot, _Zombie__None): pass
class Zombie_Straight_Horizontal(_Zombie_Straight, _Zombie_OneShot, _Zombie__Horizontal): pass
class Zombie_Straight_Horizontals(_Zombie_Straight, _Zombie_OneShot, _Zombie__Horizontals): pass
class Zombie_Straight_Vertical(_Zombie_Straight, _Zombie_OneShot, _Zombie__Vertical): pass
class Zombie_Straight_Verticals(_Zombie_Straight, _Zombie_OneShot, _Zombie__Verticals): pass
class Zombie_Straight_Cross(_Zombie_Straight, _Zombie_OneShot, _Zombie__Cross): pass
class Zombie_Straight_Angle30(_Zombie_Straight, _Zombie_OneShot, _Zombie__Angle30): pass
class Zombie_Straight_Angle30s(_Zombie_Straight, _Zombie_OneShot, _Zombie__Angle30s): pass
class Zombie_Straight_Angle45(_Zombie_Straight, _Zombie_OneShot, _Zombie__Angle45): pass
class Zombie_Straight_Angle45s(_Zombie_Straight, _Zombie_OneShot, _Zombie__Angle45s): pass
class Zombie_Straight_Angle60(_Zombie_Straight, _Zombie_OneShot, _Zombie__Angle60): pass
class Zombie_Straight_Angle60s(_Zombie_Straight, _Zombie_OneShot, _Zombie__Angle60s): pass
class Zombie_Straight_Star(_Zombie_Straight, _Zombie_OneShot, _Zombie__Star): pass
class Zombie_Straight_Target(_Zombie_Straight, _Zombie_OneShot, _Zombie__Target): pass
class Zombie_Straight_TargetCross(_Zombie_Straight, _Zombie_OneShot, _Zombie__TargetCross): pass
class Zombie_Straight_TargetAngle45s(_Zombie_Straight, _Zombie_OneShot, _Zombie__TargetAngle45s): pass
class Zombie_Straight_Horizontals_Verticals(_Zombie_Straight, _Zombie_TwoShot, _Zombie__Horizontals, _Zombie___Verticals): pass
class Zombie_Straight_Cross_Angle45s(_Zombie_Straight, _Zombie_TwoShot, _Zombie__Cross, _Zombie___Angle45s): pass
class Zombie_Straight_Star_Target(_Zombie_Straight, _Zombie_TwoShot, _Zombie__Star, _Zombie___Target): pass
class Zombie_Straight_Target_Cross(_Zombie_Straight, _Zombie_TwoShot, _Zombie__Target, _Zombie___Cross): pass
class Zombie_Straight_Target_Angle45s(_Zombie_Straight, _Zombie_TwoShot, _Zombie__Target, _Zombie___Angle45s): pass

class Zombie_Shift_None(_Zombie_Shift, _Zombie_OneShot, _Zombie__None): pass
class Zombie_Shift_Horizontal(_Zombie_Shift, _Zombie_OneShot, _Zombie__Horizontal): pass
class Zombie_Shift_Horizontals(_Zombie_Shift, _Zombie_OneShot, _Zombie__Horizontals): pass
class Zombie_Shift_Vertical(_Zombie_Shift, _Zombie_OneShot, _Zombie__Vertical): pass
class Zombie_Shift_Verticals(_Zombie_Shift, _Zombie_OneShot, _Zombie__Verticals): pass
class Zombie_Shift_Cross(_Zombie_Shift, _Zombie_OneShot, _Zombie__Cross): pass
class Zombie_Shift_Angle30(_Zombie_Shift, _Zombie_OneShot, _Zombie__Angle30): pass
class Zombie_Shift_Angle30s(_Zombie_Shift, _Zombie_OneShot, _Zombie__Angle30s): pass
class Zombie_Shift_Angle45(_Zombie_Shift, _Zombie_OneShot, _Zombie__Angle45): pass
class Zombie_Shift_Angle45s(_Zombie_Shift, _Zombie_OneShot, _Zombie__Angle45s): pass
class Zombie_Shift_Angle60(_Zombie_Shift, _Zombie_OneShot, _Zombie__Angle60): pass
class Zombie_Shift_Angle60s(_Zombie_Shift, _Zombie_OneShot, _Zombie__Angle60s): pass
class Zombie_Shift_Star(_Zombie_Shift, _Zombie_OneShot, _Zombie__Star): pass
class Zombie_Shift_Target(_Zombie_Shift, _Zombie_OneShot, _Zombie__Target): pass
class Zombie_Shift_TargetCross(_Zombie_Shift, _Zombie_OneShot, _Zombie__TargetCross): pass
class Zombie_Shift_TargetAngle45s(_Zombie_Shift, _Zombie_OneShot, _Zombie__TargetAngle45s): pass
class Zombie_Shift_Horizontals_Verticals(_Zombie_Shift, _Zombie_TwoShot, _Zombie__Horizontals, _Zombie___Verticals): pass
class Zombie_Shift_Cross_Angle45s(_Zombie_Shift, _Zombie_TwoShot, _Zombie__Cross, _Zombie___Angle45s): pass
class Zombie_Shift_Star_Target(_Zombie_Shift, _Zombie_TwoShot, _Zombie__Star, _Zombie___Target): pass
class Zombie_Shift_Target_Cross(_Zombie_Shift, _Zombie_TwoShot, _Zombie__Target, _Zombie___Cross): pass
class Zombie_Shift_Target_Angle45s(_Zombie_Shift, _Zombie_TwoShot, _Zombie__Target, _Zombie___Angle45s): pass

class Zombie_Swoop_None(_Zombie_Swoop, _Zombie_OneShot, _Zombie__None): pass
class Zombie_Swoop_Horizontal(_Zombie_Swoop, _Zombie_OneShot, _Zombie__Horizontal): pass
class Zombie_Swoop_Horizontals(_Zombie_Swoop, _Zombie_OneShot, _Zombie__Horizontals): pass
class Zombie_Swoop_Vertical(_Zombie_Swoop, _Zombie_OneShot, _Zombie__Vertical): pass
class Zombie_Swoop_Verticals(_Zombie_Swoop, _Zombie_OneShot, _Zombie__Verticals): pass
class Zombie_Swoop_Cross(_Zombie_Swoop, _Zombie_OneShot, _Zombie__Cross): pass
class Zombie_Swoop_Angle30(_Zombie_Swoop, _Zombie_OneShot, _Zombie__Angle30): pass
class Zombie_Swoop_Angle30s(_Zombie_Swoop, _Zombie_OneShot, _Zombie__Angle30s): pass
class Zombie_Swoop_Angle45(_Zombie_Swoop, _Zombie_OneShot, _Zombie__Angle45): pass
class Zombie_Swoop_Angle45s(_Zombie_Swoop, _Zombie_OneShot, _Zombie__Angle45s): pass
class Zombie_Swoop_Angle60(_Zombie_Swoop, _Zombie_OneShot, _Zombie__Angle60): pass
class Zombie_Swoop_Angle60s(_Zombie_Swoop, _Zombie_OneShot, _Zombie__Angle60s): pass
class Zombie_Swoop_Star(_Zombie_Swoop, _Zombie_OneShot, _Zombie__Star): pass
class Zombie_Swoop_Target(_Zombie_Swoop, _Zombie_OneShot, _Zombie__Target): pass
class Zombie_Swoop_TargetCross(_Zombie_Swoop, _Zombie_OneShot, _Zombie__TargetCross): pass
class Zombie_Swoop_TargetAngle45s(_Zombie_Swoop, _Zombie_OneShot, _Zombie__TargetAngle45s): pass
class Zombie_Swoop_Horizontals_Verticals(_Zombie_Swoop, _Zombie_TwoShot, _Zombie__Horizontals, _Zombie___Verticals): pass
class Zombie_Swoop_Cross_Angle45s(_Zombie_Swoop, _Zombie_TwoShot, _Zombie__Cross, _Zombie___Angle45s): pass
class Zombie_Swoop_Star_Target(_Zombie_Swoop, _Zombie_TwoShot, _Zombie__Star, _Zombie___Target): pass
class Zombie_Swoop_Target_Cross(_Zombie_Swoop, _Zombie_TwoShot, _Zombie__Target, _Zombie___Cross): pass
class Zombie_Swoop_Target_Angle45s(_Zombie_Swoop, _Zombie_TwoShot, _Zombie__Target, _Zombie___Angle45s): pass


class Player(_Sprite):
	def __init__(self, position, dimensions, hitbox_dimensions, hitbox_centre, textures, blitmasks_data, polish_texture, score, lives, feathers, tar_gun, support, multiplier, multiplier_cooldown):
		_Sprite.__init__(self, position, dimensions, hitbox_dimensions, hitbox_centre, textures, blitmasks_data, polish_texture)
		
		self.score = score
		self.lives =  lives
		self.feathers = feathers
		self.tar_gun = tar_gun
		self.support = support
		self.multiplier = multiplier
		self.multiplier_cooldown = multiplier_cooldown
		
		self._invincibility_cooldown = 0
		
	def setPosition(self, position):
		(x, y) = position
		if x - self._centre_w < 0:
			x = self._centre_w
		elif x + self._centre_w >= 800:
			x = 800 - self._centre_w
		if y - self._centre_v < 50:
			y = 50 + self._centre_v
		elif y + self._centre_v >= 600:
			y = 600 - self._centre_v
			
		_Sprite.setPosition(self, (x, y))
		
	def render(self, screen, action):
		#Flicker.
		if self._invincibility_cooldown % 10 >= 5:
			return
			
		if action == ACT_DIVE:
			self._frames[0].render(self._textures, self._position, self._centre_w, self._centre_v, screen)
		else:
			self._render(screen)
			if action == ACT_SOAR:
				self._frame_swap += 2
				
		self.renderPolish(screen)
		
	def kill(self):
		self.lives -= 1
		self._invincibility_cooldown = 60
		self.tar_gun = GUN_BASE
		self.support = SPT_NONE
		return self.lives >= 0
		
	def nick(self):
		self._invincibility_cooldown = 20
		self.support = SPT_NONE
		
	def tick(self):
		self._invincibility_cooldown = max(0, self._invincibility_cooldown - 1)
		
		#Update multiplier.
		redraw_multiplier = False
		if self.multiplier_cooldown:
			self.multiplier_cooldown -= 1
			if not self.multiplier_cooldown:
				if self.multiplier > 1:
					self.multiplier -= 1
					if self.multiplier > 1:
						self.multiplier_cooldown = 60
					redraw_multiplier = True
					
		return (redraw_multiplier,)
		
	def isVulnerable(self):
		return self._invincibility_cooldown == 0
		
	def addScore(self, points):
		new_lives = ((self.score + points) / main.LIFE_VALUE) - (self.score / main.LIFE_VALUE)
		self.score += points
		if new_lives:
			self.lives += new_lives
			return True
			
class Obstacle(pygame.Rect):
	def __init__(self, left_top, width_height, velocity, texture):
		pygame.Rect.__init__(self, left_top, width_height)
		(self._velocity_x, self._velocity_y) = velocity
		self._texture = texture
		
	def render(self, screen, rect):
		r = self.clip(rect)
		working_surface = pygame.Surface(r.size, flags=pygame.constants.SWSURFACE)
		working_surface.fill((255, 255, 255))
		working_surface.blit(self._texture, (1, 1), ((r.left + 1, r.top - 49), (r.width - 2, r.height - 2)))
		
		screen.blit(working_surface, r)
		
	def tick(self):
		self.move_ip(self._velocity_x, self._velocity_y)
		
		
class Bullet(pygame.Rect):
	def __init__(self, position, velocity):
		pygame.Rect.__init__(self, position[0] - 4, position[1] - 4, 8, 8)
		(self._velocity_x, self._velocity_y) = velocity
		
	def render(self, screen):
		pygame.draw.circle(screen, (0, 0, 0), self.center, 5, 1)
		pygame.draw.circle(screen, (109, 249, 15), self.center, 4)
		
	def tick(self):
		self.move_ip(self._velocity_x, self._velocity_y)
		
class TarBullet(Bullet):
	_hidden_frames = 0
	
	def __init__(self, position, velocity):
		Bullet.__init__(self, position, velocity)
		
	def hide(self, frames):
		self._hidden_frames += frames
		
	def render(self, screen):
		if self._hidden_frames:
			self._hidden_frames -= 1
		else:
			pygame.draw.circle(screen, (31, 31, 31), self.center, 4)
			
			
class Object(pygame.Rect):
	def __init__(self, position, texture):
		pygame.Rect.__init__(self, position[0] - 16, position[1] - 16, 32, 32)
		self._texture = texture
		
	def render(self, screen):
		screen.blit(self._texture, self.topleft)
		
	def tick(self):
		self.move_ip(-7, 0)
		
class Support(Object):
	def __init__(self, position, type):
		self._type = type
		texture = None
		if type == SPT_TAR:
			texture = _SPT_TAR_TEX
		elif type == SPT_SHIELD:
			texture = _SPT_SHIELD_TEX
		elif type == SPT_RELOAD:
			texture = _SPT_RELOAD_TEX
		if type == SPT_MOVEMENT:
			texture = _SPT_MOVEMENT_TEX
		Object.__init__(self, position, texture)
		
	def trigger(self, player):
		player.support = self._type
		return OBJ_SUPPORT
		
class Powerup(Object):
	def __init__(self, position, type):
		self._type = type
		texture = None
		if type == GUN_3_SHOT:
			texture = _GUN_3_SHOT_TEX
		elif type == GUN_5_SHOT:
			texture = _GUN_5_SHOT_TEX
		elif type == GUN_3_WAY:
			texture = _GUN_3_WAY_TEX
		if type == GUN_RAPID:
			texture = _GUN_RAPID_TEX
		Object.__init__(self, position, texture)
		
	def trigger(self, player):
		player.tar_gun = self._type
		return OBJ_POWERUP
		
class BonusLife(Object):
	def __init__(self, position):
		self._type = type
		Object.__init__(self, position, _BNS_LIFE_TEX)
		
	def trigger(self, player):
		player.lives += 1
		return OBJ_LIFE
		
class BonusFeather(Object):
	def __init__(self, position):
		self._type = type
		Object.__init__(self, position, _BNS_FEATHER_TEX)
		
	def trigger(self, player):
		player.feathers += 1
		return OBJ_FEATHER
		
		
def render(texture, blitmask, position, screen):
	(pos_x, pos_y) = position
	(width, height) = blitmask.get_size()
	left = pos_x - width / 2
	top = pos_y - height / 2
	
	working_surface = pygame.Surface((width, height), flags=(pygame.constants.SRCALPHA | pygame.constants.SWSURFACE))
	working_surface.blit(texture, (0, 0), ((left, top - 50), (width, height)))
	working_surface.blit(blitmask, (0, 0), None, pygame.constants.BLEND_RGBA_SUB)
	
	screen.blit(working_surface, (left, top))
	
