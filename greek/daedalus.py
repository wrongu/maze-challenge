import random

class Daedalus(object):

	@staticmethod
	def create(Maze, size):
		start = (random.randint(0,size-1), random.randint(0,size-1))
		end = (random.randint(0,size-1), random.randint(0,size-1))
		while end == start: end = (random.randint(0,size-1), random.randint(0,size-1))

		m = Maze(size, start, end)
		m.add_all_walls()

		visited = [start]
		branches = [start]
		current = start
		# carve random path to end
		while len(branches):
			choices = [adj for adj in m.adjacent(current) if adj not in visited]
			if choices:
				next = random.choice(choices)
				m.del_wall(current, next)
				visited.append(next)
				branches.append(next)
				current = next
			else:
				current = random.choice(branches)
				branches.remove(current)
		return m
