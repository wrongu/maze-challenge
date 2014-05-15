from collections import deque

CLEAR = -1
FOG = 0
WALL = 1

class Maze(object):
	"""This Maze class is used both as part of the driver (managing fog and solver), and as an abstraction of methods
	 for python-based architects and solvers"""

	def __init__(self, size, start, end):
		"""create a new blank maze object"""
		self._size = size # always square]
		if start == end:
			raise Warning("Maze start and end set to same position")
		if self.__out_of_bounds(start[0], start[1]):
			raise IndexError("Maze start is out of bounds")
		if self.__out_of_bounds(end[0], end[1]):
			raise IndexError("Maze end is out of bounds")
		# see Maze.set_wall() for a description of the wall formats
		self._v_walls = [CLEAR] * (size * (size-1))	# _v_walls and _h_walls are initialized to all False since
		self._h_walls = [CLEAR] * (size * (size-1))	#  walls will be progressively added by the architect
		self._h_fog = [FOG] * (size * (size-1))
		self._v_fog = [FOG] * (size * (size-1))
		self._start = start # tuple of zero-indexed (row, column) tuple
		self._end = end # same format as start
		self._position = self._start # initialize the position of some solver
		self.reveal(self._position)

	def __eq__(self, other):
		return self._start == other._start and self._end == other._end and self._position == other._position and self._h_walls == other._h_walls and self._v_walls == other._v_walls

	def reset(self):
		"""add back all fog and send solver to the start"""
		self._h_fog = [FOG] * len(self._h_fog)
		self._v_fog = [FOG] * len(self._v_fog)
		self._position = self._start # initialize the position of some solver
		self.reveal(self._position)
	
	def to_architect_string(self):
		"""return the string represenatation of this maze according to the format outlined in the readme"""
		string = "%d\n%d %d\n%d %d\n" % (self._size, self._start[0], self._start[1], self._end[0], self._end[1])
		string += "".join(['1' if w==WALL else '0' for w in self._h_walls]) + "\n"
		string += "".join(['1' if w==WALL else '0' for w in self._v_walls]) + "\n"
		return string

	def to_solver_string(self):
		"""return the string represenatation of this maze (with solver's fog) according to the format outlined in the readme"""
		self.reveal(self._position)
		string = "%d\n%d %d\n%d %d\n" % (self._size, self._start[0], self._start[1], self._end[0], self._end[1])
		string += "".join(['1' if w==WALL else ('0' if w==CLEAR else '?') for w in self._h_fog]) + "\n"
		string += "".join(['1' if w==WALL else ('0' if w==CLEAR else '?') for w in self._v_fog]) + "\n"
		string += " ".join([str(x) for x in self._position]) + "\n"
		neighbor_strings = [" ".join([str(x) for x in neighbor]) for neighbor in self.options(self._position)]
		string += ",".join(neighbor_strings)
		return string

	@staticmethod
	def load_from_architect_string(maze_format_string):
		"""Load a maze as output by an Architect"""
		set_wall = {
			'1' : WALL,
			'0' : CLEAR
		}
		lines = maze_format_string.split("\n")
		size = int(lines[0])
		start = tuple(map(int, lines[1].split()))
		end = tuple(map(int, lines[2].split()))
		m = Maze(size, start, end)
		m._h_walls = map(lambda w:set_wall[w], lines[3])
		m._v_walls = map(lambda w:set_wall[w], lines[4])
		m._h_fog = [FOG] * len(m._h_walls)
		m._v_fog = [FOG] * len(m._v_walls)
		if not m.is_valid(): raise AssertionError("Loaded an invalid maze")
		return m

	@staticmethod
	def load_from_solver_string(maze_format_string):
		"""Load a maze as given by the driver to the solver"""
		set_wall = {
			'1' : WALL,
			'0' : CLEAR,
			'?' : FOG
		}
		lines = maze_format_string.split("\n")
		size = int(lines[0])
		start = tuple(map(int, lines[1].split()))
		end = tuple(map(int, lines[2].split()))
		m = Maze(size, start, end)
		m._h_fog = map(lambda w:set_wall[w], lines[3])
		m._v_fog = map(lambda w:set_wall[w], lines[4])
		m._h_walls = m._h_fog[:]
		m._v_walls = m._v_fog[:]
		m._position = tuple(map(int, lines[5].split()))
		m.reveal(m._position)
		return m

	def move_to(self, location):
		if location in self.options():
			self._position = location
			self.reveal(self._position)
		else:
			raise Warning("attempted move_to invalid location")

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

	def reveal(self, position):
		"""update fog walls to include those adjacent to position"""
		r, c = position
		if r > 0: # reveal up
			i = (r-1)*self._size + c # index of the cell whose floor is (r,c)'s ceiling
			self._h_fog = self._h_fog[:i] + [self._h_walls[i]] + self._h_fog[i+1:]
		if r < self._size-1:
			i = r*self._size + c
			self._h_fog = self._h_fog[:i] + [self._h_walls[i]] + self._h_fog[i+1:]
		if c > 0:
			i = r*(self._size-1) + c - 1
			self._v_fog = self._v_fog[:i] + [self._v_walls[i]] + self._v_fog[i+1:]
		if c < self._size-1:
			i = r*(self._size-1) + c
			self._v_fog = self._v_fog[:i] + [self._v_walls[i]] + self._v_fog[i+1:]

	def options(self, pos=None):
		"""get a list of tuples of the un-walled neighboring positions"""
		if pos == None: pos=self._position
		r,c = pos
		def wall(r2, c2):
			min_r = min(r2, r)
			min_c = min(c2, c)
			if abs(r2-r) == 1: # vertical offset; therefore horizontal wall
				if self._h_walls[min_r * self._size + min_c] == WALL:
					return True
			else:
				if self._v_walls[min_r * (self._size - 1) + min_c] == WALL:
					return True
			return False
		return [(r2,c2) for (r2,c2) in self.adjacent(pos) if not wall(r2,c2)]

	def __out_of_bounds(self,r,c):
		return r<0 or r>self._size-1 or c<0 or c>self._size-1

	def adjacent(self, pos=None):
		"""get a list of tuples of neighboring positions (walls ignored)"""
		if pos == None: pos=self._position
		r,c = pos
		return [(r2,c2) for (r2,c2) in [(r+1,c), (r-1,c), (r,c+1), (r,c-1)] if not self.__out_of_bounds(r2,c2)]

	def num_walls(self):
		"""get the total number of walls constructed"""
		return sum([1 if w==WALL else 0 for w in self._h_walls]) + sum([1 if w==WALL else 0 for w in self._v_walls])

	def add_all_walls(self):
		"""adds in every wall. useful for architects who would rather sculpt than build

		of course, the maze is immediately invalid after calling this function"""
		self._h_walls = [WALL] * len(self._h_walls)
		self._v_walls = [WALL] * len(self._v_walls)

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
		self.reveal(self._position)

	def add_wall(self, fro, to):
		"""add a wall between the given coordinates (as usual, both are zero-indexed (row,col))"""
		self.set_wall(fro, to, WALL)

	def del_wall(self, fro, to):
		"""remove the wall between the given coordinates (as usual, both are zero-indexed (row,col))"""
		self.set_wall(fro, to, CLEAR)

	def solved(self):
		return self._position == self._end

	def ascii_str(self, fog=False):
		"""make a printable ascii represenatation of the maze

		and (optionally) highlight an avatar's location"""
		# colors help from http://stackoverflow.com/a/287944/1935085 and https://mail.python.org/pipermail/python-list/2009-August/546532.html
		BLUE = '\x1b[44m'
		GREEN = '\x1b[42m'
		RED = '\x1b[41m'
		ENDC = '\x1b[0m'
		string = "   " + " ".join([str(c) for c in range(self._size)])
		string += "\n   " + "_"*(self._size * 2 - 1)
		h_walls = self._h_fog if fog else self._h_walls
		v_walls = self._v_fog if fog else self._v_walls
		h_char = {
			WALL : '_',
			CLEAR : ' ',
			FOG : '@'
		}
		v_char = {
			WALL : '|',
			CLEAR : ' ',
			FOG : '@'
		}
		for r in range(self._size):
			string += "\n%d |" % r
			for c in range(self._size):
				color = False
				if (r,c) == self._start:
					color = True
					string += GREEN
				elif (r,c) == self._end:
					color = True
					string += RED
				elif (r,c) == self._position:
					color = True
					string += BLUE
				# bottom wall
				# special case for bottom row
				if r==self._size-1:
					string += h_char[WALL]
				else:
					string += h_char[h_walls[r*self._size+c]]
				# end color after h wall (only one cell highlighted)
				if color: string += ENDC
				# right wall
				# special case for rightmost column
				if c==self._size-1:
					string += v_char[WALL]
				# special case 2: bottom row gets '_' everywhere there isn't a vert wall
				elif r==self._size-1 and v_walls[r*(self._size-1) + c]==CLEAR:
					string += h_char[WALL]
				else:
					string += v_char[v_walls[r*(self._size-1) + c]]
		string += "\nstart:(%d,%d)\nend:(%d,%d)" % (self._start[0],self._start[1],self._end[0],self._end[1])
		return string