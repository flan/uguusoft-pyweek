import locale
import threading
import pygame
import time

import data
import sprite
import textures
import level

_LEVELS = 5
_SCORES = (
 350000,
 3000000,
 225000,
 30000000,
 250000000,
)
_DELAY = 6
LIFE_VALUE = 25000000

CASUAL = 3
NORMAL = 2
DIFFICULT = 1

class Game(object):
	def __init__(self, difficulty):
		self._difficulty = difficulty
		
	def run(self, player, screen):
		self._old_background = None
		
		keys = set()
		zombies_tarred = zombies_feathered = zombies_total = bullets_fired = bullets_landed = 0
		results = None
		
		for i in xrange(_LEVELS):
			results = self._play(player, _SCORES[i], screen, i, i + 1, results, keys)
			if results is None:
				return
			zombies_tarred += results[1]
			zombies_feathered += results[2]
			zombies_total += results[3]
			bullets_fired += results[4]
			bullets_landed += results[5]
			if player.lives == -1:
				break
				
		descriptor = "%03i" % (i)
		if player.lives >= 0:
			descriptor = "%03i" % (i + 1)
			loading_screen = ResultsScreen(results, _SCORES[i], descriptor, self._old_background, textures.LYR_FEATHER_TEX, player, screen, _DELAY)
			loading_screen.start()
			loading_screen.join()
			
		return (zombies_tarred, zombies_feathered, zombies_total, bullets_fired, bullets_landed, descriptor)
		
	def _play(self, player, target_score, screen, old_level, new_level, results, keys):
		old_descriptor = "%03i" % (old_level)
		new_descriptor = "%03i" % (new_level)
		
		self._new_background = pygame.image.load(data.filepath('background-level-%s.jpg' % (new_descriptor)))
		if self._old_background:
			loading_screen = ResultsScreen(results, target_score, old_descriptor, self._old_background, self._new_background, player, screen, _DELAY)
			loading_screen.start()
			
		_level = level.Level(new_descriptor, self._difficulty, player, self._new_background)
		if self._old_background:
			loading_screen.join()
		self._old_background = self._new_background
		
		return _level.run(screen, keys)
		
class ResultsScreen(threading.Thread):
	def __init__(self, results, target_score, old_level, old_image, new_image, player, screen, delay):
		threading.Thread.__init__(self)
		self._old_image = old_image
		self._new_image = new_image
		self._player = player
		self._screen = screen
		self._delay = delay
		
		large_font = pygame.font.Font(data.filepath('font-Windsong.ttf'), 80)
		medium_font = pygame.font.Font(data.filepath('font-Windsong.ttf'), 70)
		small_font = pygame.font.Font(data.filepath('font-DejaVuSans.ttf'), 20)
		
		(points, zombies_tarred, zombies_feathered, zombies_total, bullets_fired, bullets_landed, descriptor) = results
		weapon_accuracy = (bullets_landed / max(float(bullets_fired), 1.0))
		letter = _computeGrade(points, target_score, weapon_accuracy, zombies_tarred, zombies_feathered, zombies_total)
		
		result_header = large_font.render("Level %i clear!" % (int(old_level)), True, (0, 0, 0))
		result_score_label = small_font.render("Points earned:", True, (0, 0, 0))
		result_score = small_font.render(locale.format("%d", points, 1), True, (0, 0, 0))
		result_zombies_total_label = small_font.render("Zombies spotted:", True, (0, 0, 0))
		result_zombies_total = small_font.render(str(zombies_total), True, (0, 0, 0))
		result_zombies_tarred_label = small_font.render("Zombies tarred:", True, (0, 0, 0))
		result_zombies_tarred = small_font.render(str(zombies_tarred), True, (0, 0, 0))
		result_zombies_feathered_label = small_font.render("Zombies feathered:", True, (0, 0, 0))
		result_zombies_feathered = small_font.render(str(zombies_feathered), True, (0, 0, 0))
		result_bullets_fired_label = small_font.render("Tar-gun blasts:", True, (0, 0, 0))
		result_bullets_fired = small_font.render(locale.format("%d", bullets_fired, 1), True, (0, 0, 0))
		result_bullets_accuracy_label = small_font.render("Tar-gun accuracy:", True, (0, 0, 0))
		result_bullets_accuracy = small_font.render("%.1f%%" % (weapon_accuracy * 100.0), True, (0, 0, 0))
		result_overall = medium_font.render("Grade: %s" % (letter), True, (0, 0, 0))
		
		self._result_surface = pygame.Surface((400, 350), flags=(pygame.constants.SRCALPHA | pygame.constants.SWSURFACE))
		self._result_surface.fill((255, 255, 255, 255))
		self._result_surface.fill((63, 63, 63, 63), (1, 1, 398, 348))
		self._result_surface.blit(result_header, ((398 - result_header.get_width()) / 2, 2))
		self._result_surface.blit(result_score_label, (4, 80))
		self._result_surface.blit(result_score, (210, 80))
		self._result_surface.blit(result_zombies_total_label, (4, 105))
		self._result_surface.blit(result_zombies_total, (210, 105))
		self._result_surface.blit(result_zombies_tarred_label, (4, 130))
		self._result_surface.blit(result_zombies_tarred, (210, 130))
		self._result_surface.blit(result_zombies_feathered_label, (4, 155))
		self._result_surface.blit(result_zombies_feathered, (210, 155))
		self._result_surface.blit(result_bullets_fired_label, (4, 180))
		self._result_surface.blit(result_bullets_fired, (210, 180))
		self._result_surface.blit(result_bullets_accuracy_label, (4, 205))
		self._result_surface.blit(result_bullets_accuracy, (210, 205))
		self._result_surface.blit(result_overall, (395 - result_overall.get_width(), 348 - result_overall.get_height()))
		
	def run(self):
		clock = pygame.time.Clock()
		for i in xrange(self._delay * 20):
			clock.tick(20)
			offset = int(((i + 1) / (-self._delay * 20.0)) * 800)
			self._screen.blit(self._old_image, (offset, 50))
			self._screen.blit(self._new_image, (800 + offset, 50))
			
			#Render the player.
			self._player.render(self._screen, sprite.ACT_NONE)
			
			#Display the stage results.
			self._screen.blit(self._result_surface, (200, 150))
			
			pygame.display.flip()
			
			
def _computeGrade(points, target_points, weapon_accuracy, zombies_tarred, zombies_feathered, zombies_total):
	grade = (points / float(target_points)) * 0.1
	grade += weapon_accuracy * 0.1
	grade += (zombies_tarred / max(float(zombies_total * 0.75), 1.0)) * 0.5
	grade += (zombies_feathered / max(float(zombies_total * 0.25), 1.0)) * 0.3
	if grade >= 0.5:
		if grade >= 0.6:
			if grade >= 0.7:
				if grade >= 0.8:
					if grade >= 0.9:
						return 'S'
					else:
						return 'A'
				else:
					return 'B'
			else:
				return 'C'
		else:
			return 'D'
	else:
		return 'F'
		
		
class Conclusion(object):
	def __init__(self, results, player, difficulty):
		(self._zombies_tarred, self._zombies_feathered, self._zombies_total, self._bullets_fired, self._bullets_landed, self._levels_cleared) = results
		self._player = player
		self._difficulty = difficulty
		
	def run(self, screen):
		pygame.display.set_caption("Angel-G - Summary")
		
		#Transition.
		working_surface = pygame.Surface((800, 600), flags=(pygame.constants.SRCALPHA | pygame.constants.SWSURFACE))
		working_surface.fill((0, 0, 0, 10))
		for i in xrange(30):
			screen.blit(working_surface, (0, 0))
			pygame.display.flip()
			time.sleep(0.03)
		del working_surface
		screen.fill((0, 0, 0))
		pygame.display.flip()
		
		pygame.event.get()
		
		
		#Write high score to disk.
		score_file = open(data.filepath('score.dat'))
		scores = [line.replace('\r', '').replace('\n', '') for line in score_file.readlines()]
		score_file.close()
		score_file = open(data.filepath('score.dat'), 'w')
		
		weapon_accuracy = (self._bullets_landed / max(float(self._bullets_fired), 1.0))
		letter = _computeGrade(self._player.score + max(0, self._player.lives * LIFE_VALUE), sum(_SCORES), weapon_accuracy, self._zombies_tarred, self._zombies_feathered, self._zombies_total)
		
		new_score = locale.format("%d", self._player.score, 1)
		if self._difficulty == CASUAL:
			old_score = int(scores[0].replace(',', ''))
			if self._player.score > old_score:
				scores[0] = new_score
				scores[1] = letter
				scores[2] = self._levels_cleared
		elif self._difficulty == NORMAL:
			old_score = int(scores[3].replace(',', ''))
			if self._player.score > old_score:
				scores[3] = new_score
				scores[4] = letter
				scores[5] = self._levels_cleared
		elif self._difficulty == DIFFICULT:
			old_score = int(scores[6].replace(',', ''))
			if self._player.score > old_score:
				scores[6] = new_score
				scores[7] = letter
				scores[8] = self._levels_cleared
		score_file.writelines([score + '\n' for score in scores])
		score_file.close()
		
		
		#Render the rest of the display.
		for i in xrange(10):
			result = self._checkInterrupt()
			if not result is None: return result
			
			pygame.draw.line(screen, (255, 255, 255), (0, i ** 2), (800, i ** 2))
			pygame.draw.line(screen, (255, 255, 255), (0, 548 - i ** 2), (800, 548 - i ** 2))
			pygame.display.flip()
			time.sleep(0.05)
		
		#Display round stats.
		self._renderStats(screen, weapon_accuracy, letter)
		self._renderCredits(screen)
		pygame.display.flip()
		
		channel = None
		if self._player.lives >= 0:
			for i in xrange(100):
				result = self._checkInterrupt()
				if not result is None: return result
				time.sleep(0.1)
				
			screen.fill((0, 0, 0), (0, 101, 800, 349))
			pygame.display.flip()
			time.sleep(0.5)
			
			script_font = pygame.font.Font(data.filepath('font-Windsong.ttf'), 40)
			offset = 0
			for text in (
			  "And so, fifteen minutes later, all zombies at the hoedown were",
			  "slain.",
			  "What became of Angel-G? None know for certain. Some believe",
			  "he returned to his home. Others believe his rage fuels ongoing",
			  "conquests in far-away zombie homeworlds.",
			  "Only one detail is known for sure: there was nary a creampuff",
			  "left to be had in his wake.",
			):
				line = script_font.render(text, True, (255, 255, 255))
				screen.blit(line, (60, 100 + offset))
				offset += 50
			audio = pygame.mixer.Sound(data.filepath('sound-outro.ogg'))
			audio.set_volume(0.75)
			channel = audio.play()
			pygame.display.flip()
			
		while True:
			result = self._checkInterrupt()
			if not result is None:
				if channel:
					channel.stop()
				return result
			time.sleep(0.1)
			
	def _renderStats(self, screen, weapon_accuracy, letter):
		large_font = pygame.font.Font(data.filepath('font-Windsong.ttf'), 80)
		medium_font = pygame.font.Font(data.filepath('font-Windsong.ttf'), 70)
		small_font = pygame.font.Font(data.filepath('font-DejaVuSans.ttf'), 20)
		
		result_header = None
		if self._player.lives >= 0:
			result_header = large_font.render("All levels clear!", True, (255, 255, 255))
		else:
			result_header = large_font.render("Game over", True, (255, 255, 255))
		result_score_label = small_font.render("Points earned:", True, (255, 255, 255))
		result_score = small_font.render(locale.format("%d", self._player.score, 1), True, (255, 255, 255))
		result_zombies_total_label = small_font.render("Zombies spotted:", True, (255, 255, 255))
		result_zombies_total = small_font.render(str(self._zombies_total), True, (255, 255, 255))
		result_zombies_tarred_label = small_font.render("Zombies tarred:", True, (255, 255, 255))
		result_zombies_tarred = small_font.render(str(self._zombies_tarred), True, (255, 255, 255))
		result_zombies_feathered_label = small_font.render("Zombies feathered:", True, (255, 255, 255))
		result_zombies_feathered = small_font.render(str(self._zombies_feathered), True, (255, 255, 255))
		result_bullets_fired_label = small_font.render("Tar-gun blasts:", True, (255, 255, 255))
		result_bullets_fired = small_font.render(locale.format("%d", self._bullets_fired, 1), True, (255, 255, 255))
		result_bullets_accuracy_label = small_font.render("Tar-gun accuracy:", True, (255, 255, 255))
		result_bullets_accuracy = small_font.render("%.1f%%" % (weapon_accuracy * 100.0), True, (255, 255, 255))
		result_overall = medium_font.render("Overall grade: %s" % (letter), True, (255, 255, 255))
		
		screen.blit(result_header, ((800 - result_header.get_width()) / 2, 100))
		screen.blit(result_score_label, (204, 180))
		screen.blit(result_score, (410, 180))
		screen.blit(result_zombies_total_label, (204, 205))
		screen.blit(result_zombies_total, (410, 205))
		screen.blit(result_zombies_tarred_label, (204, 230))
		screen.blit(result_zombies_tarred, (410, 230))
		screen.blit(result_zombies_feathered_label, (204, 255))
		screen.blit(result_zombies_feathered, (410, 255))
		screen.blit(result_bullets_fired_label, (204, 280))
		screen.blit(result_bullets_fired, (410, 280))
		screen.blit(result_bullets_accuracy_label, (204, 305))
		screen.blit(result_bullets_accuracy, (410, 305))
		screen.blit(result_overall, (600 - result_overall.get_width(), 315))
		
	def _renderCredits(self, screen):
		large_font = pygame.font.Font(data.filepath('font-Windsong.ttf'), 40)
		small_font = pygame.font.Font(data.filepath('font-DejaVuSans.ttf'), 16)
		
		label_arashi = large_font.render("Arashi", True, (255, 255, 255))
		label_flan = large_font.render("Red HamsterX", True, (255, 255, 255))
		credit_arashi = small_font.render("Direction, Art Design, Scripting", True, (255, 255, 255))
		credit_flan = small_font.render("Programming, Voice, Scripting", True, (255, 255, 255))
		
		pos_arashi = 395 - credit_arashi.get_width()
		pos_flan = 404
		
		screen.blit(label_arashi, (pos_arashi - 15, 550))
		screen.blit(credit_arashi, (pos_arashi, 581))
		screen.blit(label_flan, (pos_flan, 550))
		screen.blit(credit_flan, (pos_flan + 15, 581))
		
	def _checkInterrupt(self):
		for event in pygame.event.get():
			if event.type == pygame.KEYUP:
				if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_LCTRL, pygame.K_ESCAPE):
					return True
			elif event.type == pygame.QUIT:
				return False
				
class Introduction(object):
	def run(self, screen):
		backup_screen = screen.copy()
		try:
			#Transition.
			screen.fill((255, 255, 255))
			pygame.display.flip()
			
			pygame.event.get()
			
			#Render the display.
			for i in xrange(10):
				result = self._checkInterrupt()
				if not result is None: return result
			
				pygame.draw.line(screen, (0, 0, 0), (0, i ** 2), (800, i ** 2))
				pygame.draw.line(screen, (0, 0, 0), (0, 599 - i ** 2), (800, 599 - i ** 2))
				pygame.display.flip()
				time.sleep(0.025)
				
			script_font = pygame.font.Font(data.filepath('font-Windsong.ttf'), 40)
			
			channel = None
			offset = 0
			for (text, audio) in zip(
			 (
			  "Legends speak of a sacred event...",
			  "An event never glimpsed by any mortal...",
			  "A strange nexus forms when worlds collide...",
			  "The bi-centennial, cross-dimension hoedown!",
			 ),
			 (
			  pygame.mixer.Sound(data.filepath('sound-intro-1.ogg')),
			  pygame.mixer.Sound(data.filepath('sound-intro-2.ogg')),
			  pygame.mixer.Sound(data.filepath('sound-intro-3.ogg')),
			  pygame.mixer.Sound(data.filepath('sound-intro-4.ogg')),
			 )
			):
				line = script_font.render(text, True, (0, 0, 0))
				screen.blit(line, ((800 - line.get_width()) / 2, 100 + offset))
				pygame.display.flip()
				audio.set_volume(0.75)
				channel = audio.play()
				offset += 115
				while channel.get_busy():
					result = self._checkInterrupt()
					if not result is None:
						channel.stop()
						return result
					time.sleep(0.1)
				
			for (text, audio) in zip(
			 ( 
			  (
				"Our story begins here, where punk-face zombies were eatin'",
				"all the food. Even the creampuffs. Now, the other heavenly",
				"attendees, they wisely turned a blind eye to this behaviour.",
				"Not so for Angel-G, however. He just loves those creampuffs,",
				"man! Our... \"hero\" was always such a nice, quiet man, but",
				"this... this was too much! Being denied his favourite bite-",
				"sized snackish morcels drove him to vow vengence with seething",
				"rage.",
			  ),
			  (
			   "Now, Angel-G is on a mission. A mission to bring humiliation",
			   "and defeat to his puff-snarfin' zombie foes.",
			   "",
			   "His plan? Tar-and-feather all their rotting hides.",
			   "",
			   "",
			   "Angel-G be shootin' freakin' oil, yo!",
			  )
			 ),
			 (
			  pygame.mixer.Sound(data.filepath('sound-intro-5.ogg')),
			  pygame.mixer.Sound(data.filepath('sound-intro-6.ogg')),
			 )
			):
				screen.fill((255, 255, 255), (0, 100, 800, 417))
				offset = 0
				for sub_text in text:
					line = script_font.render(sub_text, True, (0, 0, 0))
					screen.blit(line, (60, 100 + offset))
					offset += 50
				pygame.display.flip()
				audio.set_volume(0.75)
				channel = audio.play()
				while channel.get_busy():
					result = self._checkInterrupt()
					if not result is None:
						channel.stop()
						return result
					time.sleep(0.1)
		finally:
			screen.blit(backup_screen, (0, 0))
			pygame.display.flip()
		return True
		
	def _checkInterrupt(self):
		for event in pygame.event.get():
			if event.type == pygame.KEYUP:
				if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_LCTRL, pygame.K_ESCAPE):
					return True
			elif event.type == pygame.QUIT:
				return False
				
				
class TitleScreen(object):
	_tip = 0
	_selected_mode = NORMAL
	
	def run(self, screen):
		pygame.display.set_caption("Angel-G - Title")
		
		screen.fill((255, 255, 255))
		pygame.display.flip()
		time.sleep(0.15)
		
		#Draw arc.
		for i in xrange(238):
			offset = i * 5
			pygame.draw.line(screen, (0, 0, 0), (0, 0), (800, offset))
			pygame.display.flip()
		#Load tips and scores.
		tips_file = open(data.filepath('tips.txt'))
		self._tips = tuple([tuple(line.replace('\r', '').replace('\n', '').split('|')) for line in tips_file.readlines()[:-1]])
		tips_file.close()
		score_file = open(data.filepath('score.dat'))
		self._scores = tuple([line.replace('\r', '').replace('\n', '') for line in score_file.readlines()])
		score_file.close()
		#And the fonts.
		self._script_font = pygame.font.Font(data.filepath('font-Windsong.ttf'), 40)
		self._menu_font = pygame.font.Font(data.filepath('font-DejaVuSans.ttf'), 24)
		self._answer_font = pygame.font.Font(data.filepath('font-DejaVuSans.ttf'), 15)
		self._score_font = pygame.font.Font(data.filepath('font-DejaVuSans.ttf'), 20)
		
		#Draw the menu.
		for i in xrange(10):
			pygame.draw.line(screen, (127, 127, 127), (100 + i * 20, 200), (100 + (i + 1) * 20, 200))
			pygame.draw.line(screen, (127, 127, 127), (100, 200 + i * 10), (100, 200 + (i + 1) * 10))
			pygame.draw.line(screen, (127, 127, 127), (800 - i * 40, 512), (800 - (i + 1) * 40, 512))
			pygame.draw.line(screen, (127, 127, 127), (400, 600 - i * 9), (400, 600 - (i + 1) * 9))
			pygame.display.flip()
			time.sleep(0.025)
		for i in xrange(10):
			screen.fill((0, 0, 0), (101, 201, 199, int(((i + 1) / 10.0) * 99.0)))
			screen.fill((239, 239, 239), (401, 513, int(((i + 1) / 10.0) * 399.0), 87))
			pygame.display.flip()
			time.sleep(0.025)
			
		audio = pygame.mixer.Sound(data.filepath('sound-spinnaz.ogg'))
		audio.set_volume(0.75)
		audio.play()
		screen.blit(pygame.image.load(data.filepath('title-logo.png')),(400, 40))
		
		self._renderMenu(screen)
		self._renderTip(screen)
		pygame.display.flip()
		
		#Quietly load textures while the user is distracted.
		textures.init()
		
		tip_cycle = 0
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return None
				elif event.type == pygame.KEYUP:
					redraw_menu = False
					if event.key == pygame.K_UP:
						self._selected_mode += 1
						if self._selected_mode == 4:
							self._selected_mode = 0
						redraw_menu = True
					elif event.key == pygame.K_DOWN:
						self._selected_mode -= 1
						if self._selected_mode == -1:
							self._selected_mode = CASUAL
						redraw_menu = True
					elif event.key == pygame.K_RETURN:
						if self._selected_mode == 0:
							introduction = Introduction()
							if not Introduction().run(screen): return None
						else:
							return self._selected_mode
							
					if redraw_menu:
						self._renderMenu(screen)
						pygame.display.flip()
						
			tip_cycle += 1
			if tip_cycle == 100:
				tip_cycle = 0
				self._renderTip(screen)
				pygame.display.flip()
			time.sleep(0.05)
			
	def _renderMenu(self, screen):
		screen.fill((0, 0, 0), (101, 201, 198, 98))
		intro_colour = casual_colour = normal_colour = difficult_colour = (255, 255, 255)
		score = grade = level = None
		if self._selected_mode == CASUAL:
			casual_colour = (127, 127, 127)
			(score, grade, level) = self._scores[0:3]
		elif self._selected_mode == NORMAL:
			normal_colour = (127, 127, 127)
			(score, grade, level) = self._scores[3:6]
		elif self._selected_mode == DIFFICULT:
			difficult_colour = (127, 127, 127)
			(score, grade, level) = self._scores[6:9]
		else:
			intro_colour = (127, 127, 127)
			
		intro = self._menu_font.render("Introduction", True, intro_colour)
		casual = self._menu_font.render("Casual", True, casual_colour)
		normal = self._menu_font.render("Normal", True, normal_colour)
		difficult = self._menu_font.render("Difficult", True, difficult_colour)
		screen.blit(intro, (102 + (198 - intro.get_width()) / 2, 200))
		screen.blit(casual, (102 + (198 - casual.get_width()) / 2, 224))
		screen.blit(normal, (102 + (198 - normal.get_width()) / 2, 248))
		screen.blit(difficult, (102 + (198 - difficult.get_width()) / 2, 272))
		
		screen.fill((255, 255, 255), (0, 500, 275, 100))
		if self._selected_mode:
			screen.blit(self._score_font.render("High score: %s" % (score), True, (0, 0, 0)), (2, 513))
			level = int(level)
			level_text = None
			if level == _LEVELS:
				level_text = "All"
			else:
				level_text = str(level)
			screen.blit(self._score_font.render("Levels cleared: %s" % (level_text), True, (0, 0, 0)), (2, 543))
			screen.blit(self._score_font.render("Overall grade: %s" % (grade), True, (0, 0, 0)), (2, 573))
			
	def _renderTip(self, screen):
		screen.fill((239, 239, 239), (401, 513, 399, 87))
		
		(question, answer) = self._tips[self._tip]
		screen.blit(self._script_font.render(question, True, (0, 0, 0)), (402, 514))
		screen.blit(self._answer_font.render(answer, True, (0, 0, 0)), (415, 582))
		
		self._tip += 1
		if self._tip == len(self._tips):
			self._tip = 0
			
