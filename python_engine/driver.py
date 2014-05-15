#!/usr/bin/python
import maze
import time
from sys import exit
import subprocess
import itertools

pipe_in = open('temp_in', 'rw')
pip_out = open('temp_out', 'rw')

# DEFINE THE ARCHITECT AND SOLVER HERE
# Architect is a program which takes input via stdin (as spec'd in readme) and outputs a maze string
architects = {
	'greek' : {
		'args' : ['./daedalus.py']
	}
}

solvers = {
	'greek' : {
		'args' : ['./minotaur.py']
	}
}

SIZE = 20
SEED = 42
STEP_LIMIT = SIZE*SIZE*SIZE

# Comment these lines if you don't want the same output every time
import random
random.seed(6)

########################################################
#### everything below this line is not customizable ####
########################################################

print "constructing architect subprocess"
architect_input  = "%d %d\n" % (SIZE, SEED)
kargs = architects['greek']
kargs.update({
		'stdin' : subprocess.PIPE,
		'stdout' : subprocess.PIPE,
		'stderr':subprocess.STDOUT
	})
architect_process = subprocess.Popen(**kargs)
architect_output = architect_process.communicate(input=architect_input)[0]
m = maze.Maze.load_from_architect_string(architect_output)
print m.ascii_str()

if not m.is_valid():
	print "Maze is invalid. Exiting."
	exit(1)

def maze_score(maze, steps_taken):
	L1_dist = abs(maze._start[0] - maze._end[0]) + abs(maze._start[1] - maze._end[1])
	if L1_dist == 0: return -1.0 # trying to cheat, eh? You get a negative score.
	n_walls = maze.num_walls()
	return float(steps_taken) / float(max(L1_dist, n_walls))

for steps in xrange(STEP_LIMIT):
	if m.solved():
		print "Solver finished in %d steps" % steps
		break
	
	solver_input = m.to_solver_string()
	kargs = solvers['greek']
	kargs.update({
		'stdin' : subprocess.PIPE,
		'stdout' : subprocess.PIPE,
		'stderr':subprocess.STDOUT
	})
	solver_process = subprocess.Popen(**kargs)
	solver_output = solver_process.communicate(input=solver_input)[0]
	print "SOLVER OUTPUT='%s'" % solver_output
	decision = tuple(map(int,solver_output.split()))
	if decision in m.options():
		m.move_to(decision)
	else:
		print "Solver tried to cheat!"
	# COMMENT THIS TO TURN OFF ANIMATION
	print m.ascii_str(fog=True); time.sleep(0.1)
else: # 'nobreak' clause of for loop
	print "Solver could not finish the maze in %d steps" % steps
print "Score: %f" % maze_score(m, steps)