# Import Python 3 style integer division
from __future__ import division

# Try to import modules
try:
	import sys, os, math, random, getopt, weakref
	import pygame
	import numpy as np
	import matplotlib.pyplot as plt
	from pygame.locals import *
	from socket import *
	

# Throw an error if a module is not loaded
except ImportError, err:
	print "%s Failed to load module: %s" % (__file__, err)
	import sys
	sys.exit(1)

class Bird(pygame.sprite.Sprite):
	"""A hawk or dove sprite. Subclasses the pygame sprite class."""
	
	def __init__(self, xy, vector):
		# initialize the pygame sprite
		pygame.sprite.Sprite.__init__(self)
		#Set an image
		self.image = pygame.Surface((8, 8))
		# Set rect
		self.rect = pygame.Rect(0, 0, 8, 8)
		self.defaultcolor = (255, 0, 0)
		self.image.fill(self.defaultcolor)		
		# set position 
		self.rect.centerx, self.rect.centery = xy
		self.area = pygame.display.get_surface().get_rect()
		self.vector = vector
		self.hit = 0
		self.fitness = 100
		self.fitspeed = self.fitness / 20
		self.name = str(id(self))
		self.roundsplayed = 0
		self.killsound = pygame.mixer.Sound('Basso.ogg')
		self.collidesound = pygame.mixer.Sound('Tink.ogg')
		

		
	def update(self):
		newpos = self.calcnewpos(self.rect, self.vector)
		self.rect = newpos
		if game.fitspeed:
			self.fitspeed = self.fitness / 20
			(angle, z) = (self.vector[0], self.fitspeed)			
		else: 
			(angle, z) = self.vector
		
		#check if the bird hits the side of the screen
		if not self.area.contains(newpos):
			tl = not self.area.collidepoint(newpos.topleft)
			tr = not self.area.collidepoint(newpos.topright)
			bl = not self.area.collidepoint(newpos.bottomleft)
			br = not self.area.collidepoint(newpos.bottomright)
			# if so, bounce it off
			if tr and tl or (br and bl):
				angle = -angle
			if tl and bl:
				#self.offcourt()
				angle = math.pi - angle
			if tr and br:
				angle = math.pi - angle	
		
		#check if the bird hits another bird	
		else:
			# Get a list of all birds, called "birdhouse"
			birdhouse = list(game.sprites)
			# Remove this bird from the birdhouse
			for thisbird in birdhouse:
				birdhouse.remove(thisbird)
				for bird in birdhouse:
					# Check if it hits another bird
					if thisbird.rect.colliderect(bird.rect):
						# If it does, play a game and bounce the bird so it doesn't continue colliding
						#print "Playing a game: %s (Fitness %d) vs. %s (Fitness %d)" % (thisbird.name, thisbird.fitness, bird.name, bird.fitness)
						thisbird.playround(bird)
						#if not pygame.mixer.get_busy(): self.collidesound.play()
						angle = math.pi - angle
						while thisbird.rect.colliderect(bird.rect):
							thisbird.rect = thisbird.rect.move(1, 0)
							bird.rect = bird.rect.move(-1, 0)
		
		#spend some fitness each turn
		#self.fitness -= .025
		game.scoreboard.update(game.hawkgroup, game.dovegroup, game.bourgeoisgroup)
		game.scoreboard.population
		self.fitness -= .025 * math.log(game.scoreboard.population)

							
		#check if the bird is dead
		if self.fitness <= game.deaththreshold:
			self.kill()
			if not pygame.mixer.get_busy(): self.killsound.play()								
		
		#check if the bird is fit enough to reproduce
		if self.fitness > game.replicationthreshold:
			splitcoord = (self.rect.centerx, self.rect.centery)
			if self.type == "Hawk":
				game.nest.launchhawk((splitcoord, random.uniform(0, 2 * math.pi )))
				game.nest.launchhawk((splitcoord, random.uniform(0, 2 * math.pi )))
			elif self.type == "Dove":
				game.nest.launchdove((splitcoord, random.uniform(0, 2 * math.pi )))
				game.nest.launchdove((splitcoord, random.uniform(0, 2 * math.pi )))
			elif self.type == "Bourgeois":
				game.nest.launchbourgeois((splitcoord, random.uniform(0, 2 * math.pi )))
				game.nest.launchbourgeois((splitcoord, random.uniform(0, 2 * math.pi )))
			self.kill()
			
		if game.fitspeed:
			self.vector = (angle, self.fitspeed)
		else:
			self.vector = (angle, z)
	
	def calcnewpos(self, rect, vector):
		if game.fitspeed:
			(angle, z) = vector
			(dx, dy) = (self.fitspeed*math.cos(angle), self.fitspeed*math.sin(angle))
		else:
			(angle, z) = vector
			(dx, dy) = (z*math.cos(angle), z*math.sin(angle))
		return rect.move(dx, dy)					

class Hawk(Bird):
	"""A hawk sprite. Subclasses the Bird class. Takes a different color."""
	def __init__(self, xy, vector):
		super(Hawk, self).__init__(xy, vector)
		#Change color to brown
		self.defaultcolor = (160, 82, 45)
		self.image.fill(self.defaultcolor)
		self.type = "Hawk"
		self.name = self.type + self.name
	
	def playround(self, opponent):
		if opponent.type == "Dove":
			#print "Hawk vs. Dove!"
			#print "Old fitness: %d" % self.fitness
			self.fitness = self.fitness + game.payoff
			#print "New fitness: %d" % self.fitness
		elif opponent.type == "Hawk":
			#print "Hawk vs. Hawk!" 
			#print "Old fitness: %d" % self.fitness
			self.fitness = self.fitness + ((game.payoff - game.cost) / 2)
			opponent.fitness = opponent.fitness + ((game.payoff - game.cost) / 2)
			#print "New fitness: %d" % self.fitness
		elif opponent.type == "Bourgeois" and opponent.rect.centerx <= 400:
			self.fitness = self.fitness +((game.payoff - game.cost) / 2)
			opponent.fitness = opponent.fitness + ((game.payoff - game.cost) / 2)
		elif opponent.type == "Bourgeois" and opponent.rect.centerx > 400:
			self.fitness = self.fitness + game.payoff
		self.roundsplayed += 1

			
class Dove(Bird):
	"""A dove sprite. Subclasses the Bird class. Takes a different color."""
	def __init__(self, xy, vector):
		super(Dove, self).__init__(xy, vector)
		#Change color to white
		self.defaultcolor = (255, 255, 255) 
		self.image.fill(self.defaultcolor)
		self.type = "Dove"
		self.name = self.type + self.name
		
	def playround(self, opponent):
		if opponent.type == "Dove":
			#print "Dove vs. Dove!"
			#print "Old fitness: %d" % self.fitness
			self.fitness = self.fitness + (game.payoff / 2)
			opponent.fitness = opponent.fitness + (game.payoff / 2)
			#print "New fitness: %d" % self.fitness
		elif opponent.type == "Hawk":
			#print "Dove vs. Hawk!"
			#print "Old fitness: %d" % self.fitness
			opponent.fitness = opponent.fitness + game.payoff
			#print "New fitness: %d" % self.fitness
		elif opponent.type == "Bourgeois" and opponent.rect.centerx <= 400:
			opponent.fitness = opponent.fitness + game.payoff
		elif opponent.type == "Bourgeois" and opponent.rect.centerx > 400:
			self.fitness = self.fitness + (game.payoff / 2)
			opponent.fitness = opponent.fitness + (game.payoff / 2)
		self.roundsplayed += 1

class Bourgeois(Bird):
	"""A bourgeois sprite. Subclasses the Bird class. Takes a different color."""
	def __init__(self, xy, vector):
		super(Bourgeois, self).__init__(xy, vector)
		#Change color to gray
		self.defaultcolor = (110, 110, 110)
		self.image.fill(self.defaultcolor)
		self.type = "Bourgeois"
		self.name = self.type + self.name
	
	def playround(self, opponent):
		if opponent.type == "Dove" and self.rect.centerx <= 400:
			#print "Aggressive B. vs. Dove!"
			#print "Old fitness: %d" % self.fitness
			self.fitness = self.fitness + game.payoff
			#print "New fitness: %d" % self.fitness
		elif opponent.type == "Dove" and self.rect.centerx > 400:
			#print "Peaceful B. vs. Dove!"
			#print "Old fitness: %d" % self.fitness
			self.fitness = self.fitness + (game.payoff / 2)
			opponent.fitness = opponent.fitness + (game.payoff / 2)
			#print "New fitness: %d" % self.fitness
		elif opponent.type == "Hawk" and self.rect.centerx <= 400:
			#print "Aggressive B. vs. Hawk!" 
			#print "Old fitness: %d" % self.fitness
			self.fitness = self.fitness + ((game.payoff - game.cost) / 2)
			opponent.fitness = opponent.fitness + ((game.payoff - game.cost) / 2)
		elif opponent.type == "Hawk" and self.rect.centerx > 400:
			#print "Peaceful B. vs Hawk!"
			opponent.fitness = opponent.fitness + game.payoff			
			#print "New fitness: %d" % self.fitness
		self.roundsplayed += 1
		
class Scoreboard(object):
	"""A simple object to keep track of the population of birds and their average fitness."""
	
	def update(self, hawkspritegroup, dovespritegroup, bourgeoisspritegroup):
	
		self.hawkpop = len(hawkspritegroup)
		self.dovepop = len(dovespritegroup)
		self.bourpop = len(bourgeoisspritegroup)
		self.population = (self.hawkpop + self.dovepop + self.bourpop)
		
		if self.population > 0:
			self.hawkpercent = (self.hawkpop / self.population) * 100
		else: self.hawkpercent = 0
		
		if self.population > 0:
			self.dovepercent = (self.dovepop / self.population) * 100
			
		if self.population > 0:
			self.bourpercent = (self.bourpop / self.population) * 100
		else: self.bourpercent = 0
		
		if self.hawkpop > 0:
			self.hawkavgfitness = (sum(hawk.fitness for hawk in hawkspritegroup)) / (self.hawkpop)
		else: self.hawkavgfitness = 0
		
		if self.dovepop > 0:
			self.doveavgfitness = (sum(dove.fitness for dove in dovespritegroup)) / (self.dovepop)
		else: self.doveavgfitness = 0
		
		if self.bourpop > 0:
			self.bouravgfitness = (sum(bour.fitness for bour in bourgeoisspritegroup)) / (self.bourpop)
		else: self.bouravgfitness = 0
		
		if (sum(hawk.roundsplayed for hawk in hawkspritegroup)) > 0: 
			self.hawkavgpayoff = self.hawkavgfitness / (sum(hawk.roundsplayed for hawk in hawkspritegroup))
		else: self.hawkavgpayoff = 0
		
		if (sum(dove.roundsplayed for dove in dovespritegroup)) > 0: 
			self.doveavgpayoff = self.doveavgfitness / (sum(dove.roundsplayed for dove in dovespritegroup))
		else: self.doveavgpayoff = 0	
		
		if (sum(bour.roundsplayed for bour in bourgeoisspritegroup)) > 0: 
			self.bouravgpayoff = self.bouravgfitness / (sum(bour.roundsplayed for bour in bourgeoisspritegroup))
		else: self.bouravgpayoff = 0	
		
	def printscores(self):
		print "\n"
		print "Population: %d" % self.population
		print "Hawks: %d (%d percent)." % (self.hawkpop, self.hawkpercent)
		print "Avg. Fitness: %d. Avg. Payoff: %d." % (self.hawkavgfitness, self.hawkavgpayoff)
		
		print "Doves: %d (%d percent)." % (self.dovepop, self.dovepercent)
		print "Avg. Fitness: %d. Avg Payoff: %d." % (self.doveavgfitness, self.doveavgpayoff)
		
		print "Bourgeois: %d (%d percent)." % (self.bourpop, self.bourpercent)
		print "Avg. Fitness: %d. Avg Payoff: %d." % (self.bouravgfitness, self.bouravgpayoff)
		
			
class Nest(object):
	"""The Nest generates new Birds."""
	def __init__(self):
		self.hatchsound = pygame.mixer.Sound('Pop.ogg')

	def getcoordinates(self):
		randcoord = random.randint(0, game.windowlength), random.randint(0, game.windowheight)
		randangle = random.uniform(0, 2 * math.pi )
		return (randcoord, randangle)

	def launchdove(self, (randcoord, randangle)):
		if game.fitspeed:
			speed = 300 
		else: speed = game.speed
		game.scoreboard.update(game.hawkgroup, game.dovegroup, game.bourgeoisgroup)
		if game.scoreboard.population <= 60:
			newdove = Dove((randcoord),(randangle, speed))
			game.sprites.add(newdove)
			game.dovegroup.add(newdove)
			if not pygame.mixer.get_busy(): self.hatchsound.play()
		else: print "Too many birds!"

	def launchhawk(self, (randcoord, randangle)):
		if game.fitspeed:
			speed = 100 
		else: speed = game.speed
		game.scoreboard.update(game.hawkgroup, game.dovegroup, game.bourgeoisgroup)
		if game.scoreboard.population <= 60:
			newhawk = Hawk((randcoord),(randangle, speed))
			game.sprites.add(newhawk)
			game.hawkgroup.add(newhawk)	
			if not pygame.mixer.get_busy(): self.hatchsound.play()
		else: print "Too many birds!"
		
	def launchbourgeois(self, (randcoord, randangle)):
		if game.fitspeed:
			speed = 100 
		else: speed = game.speed
		game.scoreboard.update(game.hawkgroup, game.dovegroup, game.bourgeoisgroup)
		if game.scoreboard.population <= 60:
			newbourgeois = Bourgeois((randcoord),(randangle, speed))
			game.sprites.add(newbourgeois)
			game.bourgeoisgroup.add(newbourgeois)
			if not pygame.mixer.get_busy(): self.hatchsound.play()
		else: print "Too many birds!"
	
class Game(object):
	"""A simple object that initializes pygame and sets up the game to run."""
	
	def __init__(self):
		"""Called when the Game object is initialized. Initializes pygame and sets up a pygame window and other pygame tools."""
	
		# Load and set up pygame
		pygame.init()
	
		# Create a game window
		self.windowlength = 640
		self.windowheight = 480
		self.window = pygame.display.set_mode((self.windowlength, self.windowheight))
	
		# Create a clock
		self.clock = pygame.time.Clock()
	
		# Set the window title
		pygame.display.set_caption("Hawk & Dove")
	
		# Initialize the sound mixer and load sounds
		self.mixer = pygame.mixer.init()
		
		# Tell pygame to pay attention only to certain events.
		pygame.event.set_allowed([QUIT, KEYDOWN])
		
		# Make a background -- all black
		self.background = pygame.Surface((self.windowlength, self.windowheight))
		self.background.fill((0, 0, 0))
		
		# Flip the display so the background is shown
		pygame.display.flip()
		
		# Create a sprite rendering group for the hawk and dove
		self.sprites = pygame.sprite.RenderUpdates()
		
		# Create hawk and dove sprite groups
		self.hawkgroup = pygame.sprite.Group()
		self.dovegroup = pygame.sprite.Group()
		self.bourgeoisgroup = pygame.sprite.Group()
		
		# Build a Nest
		self.nest = Nest()
		
		# Create a scoreboard.
		self.scoreboard = Scoreboard()
		
		# Set the payoff, cost, death threshold and replication threshold
		self.payoff = 10
		self.cost = 20
		self.deaththreshold = 0
		self.replicationthreshold = 200
		
		# Set default bird speed to 5
		self.speed = 5
		
		# Set fitspeeds to false
		self.fitspeed = False
	
	def run(self):
		"""Runs the game. Contains the pygame loop that computes and renders each frame."""
	
		print "Starting event loop"
	
		running = True
		# Run until something tells the loop to stop
		while running:
		
			# Tick the pygame clock. Limit FPS by passing the desired frames per second.
			self.clock.tick(60)
		
			# Handle pygame events. If user closes the game, stop running
			running = self.handleEvents()
		
			# Update the title bar with our fps
			pygame.display.set_caption("Hawk & Dove (%d fps)" % self.clock.get_fps())
			
			# Update our sprites
			for sprite in self.sprites:
				sprite.update()
				
			# Render our sprites
			self.sprites.clear(self.window, self.background)
			dirty = self.sprites.draw(self.window)
		
			# Blit the dirty areas of the screen
			pygame.display.update(dirty)
				
		print 'Quitting. Thanks for playing.'
	
	def handleEvents(self):
		"""Poll for pygame events and behave accordingly. Return false to the event loop to end the game."""
	
		# Poll for pygame events
		for event in pygame.event.get():
			if event.type == QUIT:
				return False
		
			# Handle user input
			elif event.type == KEYDOWN:
				# If the user presses escape, quit the event loop.
				if event.key == K_ESCAPE:
					return False
				if event.key == K_h:
					#Launch a new hawk from the nest
					launchcoordinates = game.nest.getcoordinates()
					game.nest.launchhawk(launchcoordinates)
														
				if event.key == K_d:
					# Launch a new dove from the nest
					launchcoordinates = game.nest.getcoordinates()
					game.nest.launchdove(launchcoordinates)
					
				if event.key == K_b:
					# Launch a new bourgeois from the nest
					launchcoordinates = game.nest.getcoordinates()
					game.nest.launchbourgeois(launchcoordinates)

				if event.key == K_p:
					# Print population statistics
					game.scoreboard.update(game.hawkgroup, game.dovegroup, game.bourgeoisgroup)
					game.scoreboard.printscores()	
					
				if event.key == K_k:
					for bird in game.sprites:
						if bird.fitness < 10:
							bird.kill()
							
				if event.key == K_n:
					for bird in game.sprites:
						if bird.fitness > 10:
							bird.kill()
							for newbird in range(0, int(bird.fitness / 70)):
								launchcoordinates = game.nest.getcoordinates()
								if bird.type == "Hawk":
									game.nest.launchhawk(launchcoordinates)
								elif bird.type == "Dove":
									game.nest.launchdove(launchcoordinates)
								elif bird.type == "Bourgeois":
									game.nest.launchbourgeois(launchcoordinates)
				
				if event.key == K_q:
					for bird in game.sprites:
						bird.kill()
				
				if event.key == K_EQUALS:
				#change d[e]ath threshold
					game.deaththreshold += 10
					print "New death threshold: %d" % game.deaththreshold
					
				if event.key == K_MINUS:
				#change d[e]ath threshold
					game.deaththreshold -= 10
					print "New death threshold: %d" % game.deaththreshold
 						
				
				if event.key == K_LEFTBRACKET:
				#change [r]eplication threshold
					game.replicationthreshold -= 10	
					print "New replication threshold: %d" % game.replicationthreshold

				
				if event.key == K_RIGHTBRACKET:
				#change [r]eplication threshold
					game.replicationthreshold += 10
					print "New replication threshold: %d" % game.replicationthreshold				
				
				if event.key == K_QUOTE:
				#change [p]ayoff
					game.payoff += 10
					print "New payoff: %d" % game.payoff
				
				if event.key == K_SEMICOLON:
					game.payoff -= 10
					print "New payoff: %d" % game.payoff
				
				if event.key == K_SLASH:
				#change [c]ost
					game.cost += 10
					print "New cost: %d" % game.cost
				
				if event.key == K_PERIOD:
				#change [c]ost
					game.cost -= 10
					print "New cost: %d" % game.cost
				
				if event.key == K_l:
				#enable log(fitness) speeds
					game.fitspeed = True
					print "fitspeed enabled."
				
				if event.key == K_k:
				#disable log(fitness) speeds
					game.fitspeed = False
					print "fitspeed disabled."
					
				if event.key == K_UP:
					game.speed += 1
					print "Speed: %d" % game.speed
				
				if event.key == K_DOWN:
					game.speed -= 1
					print "Speed: %d" % game.speed
				
				if event.key == K_z:
					print "Death threshold: %d" % game.deaththreshold
					print "Replication threshold: %d" % game.replicationthreshold				

					print "Payoff: %d" % game.payoff
					print "Cost: %d" % game.cost			
										
					
		return True

	


# Create and run a game
if __name__ == '__main__':
	game = Game()
	game.run()
		 
