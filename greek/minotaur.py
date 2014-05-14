import random

class Minotaur(object):
	def move(self, position, choices, goal):
		# the minotaur is not very smart
		return random.choice(choices)