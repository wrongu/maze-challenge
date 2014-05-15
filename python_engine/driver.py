#!/usr/bin/python
import maze
import subprocess
import itertools

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
VERBOSE = True
STEP_LIMIT = SIZE*SIZE*SIZE

########################################################
#### everything below this line is not customizable ####
########################################################

def maze_score(maze, steps_taken):
	L1_dist = abs(maze._start[0] - maze._end[0]) + abs(maze._start[1] - maze._end[1])
	if L1_dist == 0: return -1.0 # trying to cheat, eh? You get a negative score.
	n_walls = maze.num_walls()
	return float(steps_taken) / float(max(L1_dist, n_walls))

# get all pairs of architect+solver
all_matches = itertools.product(architects.keys(), solvers.keys())
architect_input  = "%d %d\n" % (SIZE, SEED)

with open('stats.txt', 'w') as f:
	for arch_name, solver_name in all_matches:
		try:
			if VERBOSE: print "beginning match", arch_name, "vs", solver_name
			kargs = architects[arch_name]
			kargs.update({
					'stdin' : subprocess.PIPE,
					'stdout' : subprocess.PIPE,
					'stderr':subprocess.STDOUT
				})
			architect_process = subprocess.Popen(**kargs)
			architect_output = architect_process.communicate(input=architect_input)[0]
			m = maze.Maze.load_from_architect_string(architect_output)
			if VERBOSE: print m.ascii_str()

			if not m.is_valid():
				raise AssertionError("Invalid Maze")

			for steps in xrange(STEP_LIMIT):
				if m.solved():
					if VERBOSE: print "Solver finished in %d steps" % steps
					break
				elif steps % SIZE == 0 and VERBOSE:
					print steps
				
				solver_input = m.to_solver_string()
				kargs = solvers['greek']
				kargs.update({
					'stdin' : subprocess.PIPE,
					'stdout' : subprocess.PIPE,
					'stderr':subprocess.STDOUT
				})
				solver_process = subprocess.Popen(**kargs)
				solver_output = solver_process.communicate(input=solver_input)[0]
				decision = tuple(map(int,solver_output.split()))

				if decision in m.options():
					m.move_to(decision)
				elif VERBOSE: print "Solver tried to cheat!" # not an exception.. already limited by STEP_LIMIT
			else: # 'nobreak' clause of for loop
				if VERBOSE: print "Solver could not finish the maze in %d steps" % steps
			score = maze_score(m, steps)
			scoreline = "%s,%s,%d,%d,%f,%f" % (arch_name, solver_name, SIZE, SEED, score, 1/score)
			if VERBOSE: print scoreline
			f.write(scoreline+"\n")
		except Exception as e:
			print "Problem with match", arch_name, "vs", solver_name, "::", e