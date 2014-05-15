#!/usr/bin/python
import maze
import random
import sys

args = sys.stdin.readlines()
foggy_maze = maze.Maze.load_from_solver_string(''.join(args))

# the minotaur is not very clever
decision = random.choice(foggy_maze.options())

# print output to stdout
print " ".join(map(str, decision))