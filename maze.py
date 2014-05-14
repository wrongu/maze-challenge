from collections import deque

class Maze(object):

	def __init__(self, size, start, end):
		"""create a new blank maze object"""
		self._size = size # always square]
		if start == end:
			raise Warning("Maze start and end set to same position")
		if self.__out_of_bounds(*start):
			raise IndexError("Maze start is out of bounds")
		if self.__out_of_bounds(*end):
			raise IndexError("Maze end is out of bounds")
		# see Maze.set_wall() for a description of the wall formats
		self._v_walls = [False] * (size * (size-1))	# _v_walls and _h_walls are initialized to all False since
		self._h_walls = [False] * (size * (size-1))	#  walls will be progressively added by the architect
		self._start = start # tuple of zero-indexed (row, column) tuple
		self._end = end # same format as start

	def is_valid(self):
		"""return whether there is a path from start to end"""
		# breadth-first search
		visited = [[False]*self._size for s in range(self._size)] # grid of locations marked 'visited'
		Q = deque()
		Q.append(self._start)
		while len(Q) > 0:
			current = Q.pop()
			if current == self._end:
				return True
			visited[current[0]][current[1]] = True # mark this spot as visited
			# get all neighbors who haven't been visited yet
			neighbors = [pt for pt in self.options(current) if not visited[pt[0]][pt[1]]]
			# append said neighbors to the search queue
			for n in neighbors: Q.append(n)
		return False # if we reached here, then the queue was exhausted without ever finding a path

	def options(self, position):
		"""get a list of tuples of the un-walled neighboring positions"""
		r,c = position
		def wall(r2, c2):
			min_r = min(r2, r)
			min_c = min(c2, c)
			if abs(r2-r) == 1: # vertical offset; therefore horizontal wall
				if self._h_walls[min_r * self._size + min_c]:
					return True
			else:
				if self._v_walls[min_r * (self._size - 1) + min_c]:
					return True
			return False
		return [(r2,c2) for (r2,c2) in self.adjacent(position) if not wall(r2,c2)]

	def __out_of_bounds(self,r,c):
		return r<0 or r>self._size-1 or c<0 or c>self._size-1

	def adjacent(self, position):
		"""get a list of tuples of neighboring positions (walls ignored)"""
		r,c = position
		return [(r2,c2) for (r2,c2) in [(r+1,c), (r-1,c), (r,c+1), (r,c-1)] if not self.__out_of_bounds(r2,c2)]

	def num_walls(self):
		"""get the total number of walls constructed"""
		# this takes advantage of the fact that False=0 and True=1 in arithmetic operations
		return sum(self._v_walls) + sum(self._h_walls)

	def add_all_walls(self):
		"""adds in every wall. useful for architects who would rather sculpt than build

		of course, the maze is immediately invalid after calling this function"""
		self._h_walls = [True] * len(self._h_walls)
		self._v_walls = [True] * len(self._v_walls)

	def set_wall(self, fro, to, value):
		"""directly set the value of a wall between the given coordinates. helper function for add_wall() and del_wall()

			A | B | C | D ...        vertical walls separate columns (A to B, F to G). horizontal walls separate rows (B to F, D to H).
		   --- --- --- ---           _h_walls and _v_walls are flattened 2D arrays of horizontal and vertical walls, respectively, and 
			E | F | G | H ...        they correspond to the RIGHT and DOWN from flagged indices. A|B would be a vertical wall on A. On
		   --- --- --- ---           a maze with C columns, there are C-1 vertical walls per row. Since these mazes are square,
			.                        that makes size*(size-1) for each of h- and v-walls. Indexing into them is like any other flattened
			.                        2D array. Given (r,c), the horizontal wall to (r+1,c) is _h_walls[r*size+c], and the vertical
									 wall to (r,c+1) is _v_walls[r*(size-1)+c]."""
		rf,cf = fro
		rt,ct = to
		# check if both are in bounds
		if self.__out_of_bounds(*fro) or self.__out_of_bounds(*to):
			raise IndexError("Cannot alter wall on points outside the maze: (%d,%d)=>(%d,%d)" % (rf,cf,rt,ct))
		# check that fro and to are one space away
		dr = abs(rf-rt)
		dc = abs(cf-ct)
		if dr + dc != 1:
			raise IndexError("Cannot alter wall on non-adjacent coordinates")
		# use min-r and min-c to index into wall arrays
		min_r = min(rf, rt)
		min_c = min(cf, ct)
		if dr == 1: # change in rows is stepping up and down. that takes a horizontal wall
			self._h_walls[min_r * self._size + min_c] = value
		else: # otherwise this is a vertical wall
			self._v_walls[min_r * (self._size - 1) + min_c] = value

	def add_wall(self, fro, to):
		"""add a wall between the given coordinates (as usual, both are zero-indexed (row,col))"""
		self.set_wall(fro, to, True)

	def del_wall(self, fro, to):
		"""remove the wall between the given coordinates (as usual, both are zero-indexed (row,col))"""
		self.set_wall(fro, to, False)

	def ascii_str(self, avatar=None):
		"""make a printable ascii represenatation of the maze

		and (optionally) highlight an avatar's location"""
		# colors help from http://stackoverflow.com/a/287944/1935085 and https://mail.python.org/pipermail/python-list/2009-August/546532.html
		BLUE = '\x1b[44m'
		GREEN = '\x1b[42m'
		RED = '\x1b[41m'
		ENDC = '\x1b[0m'
		string = "   " + " ".join([str(c) for c in range(self._size)])
		string += "\n   " + "_"*(self._size * 2 - 1)
		for r in range(self._size):
			string += "\n%d |" % r
			for c in range(self._size):
				color = False
				if (r,c) == avatar:
					color = True
					string += BLUE
				elif (r,c) == self._start:
					color = True
					string += GREEN
				elif (r,c) == self._end:
					color = True
					string += RED
				# bottom wall
				string += "_" if (r==self._size-1) or (self._h_walls[r*self._size + c]) else " "
				if color:
					string += ENDC
				# right wall
				string += "|" if (c==self._size-1) or (self._v_walls[r*(self._size-1) + c]) else ("_" if (r==self._size-1) else " ")
		string += "\nstart:(%d,%d)\nend:(%d,%d)" % (self._start[0],self._start[1],self._end[0],self._end[1])
		return string