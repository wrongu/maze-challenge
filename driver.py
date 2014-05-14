import maze
import sys
import time
from greek import Architect, Solver

SIZE = 20
STEP_LIMIT = SIZE*SIZE*SIZE

# Comment these lines if you don't want the same output every time
import random
random.seed(6)

########################################################
#### everything below this line is not customizable ####
########################################################

m = Architect.create(maze.Maze, SIZE)
print m.ascii_str()

if not m.is_valid():
	print "Maze is invalid. Exiting."
	sys.exit(1)

def maze_score(maze, steps_taken):
	L1_dist = abs(maze._start[0] - maze._end[0]) + abs(maze._start[1] - maze._end[1])
	if L1_dist == 0: return -1.0 # trying to cheat, eh? You get a negative score.
	n_walls = maze.num_walls()
	return float(steps_taken) / float(max(L1_dist, n_walls))

s = Solver()
spos = m._start
for steps in xrange(STEP_LIMIT):
	if spos == m._end:
		print "Solver finished in %d steps" % steps
		break
	opts = m.options(spos)
	choice = s.move(spos, opts, m._end)
	if choice in opts:
		spos = choice
	else:
		print "Solver tried to cheat!"
	# COMMENT THIS TO TURN OFF ANIMATION
	print m.ascii_str(spos); time.sleep(0.1)
else: # 'nobreak' clause of for loop
	print "Solver could not finish the maze in %d steps" % steps
print "Score: %f" % maze_score(m, steps)