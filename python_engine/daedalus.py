#!/usr/bin/python
import maze
import random
import sys

args = map(int, sys.stdin.readline().split()) + [1234567] # 1234567 is default seed
size = args[0]
seed = args[1]

random.seed(seed)
start = (random.randint(0,size-1), random.randint(0,size-1))
end = (random.randint(0,size-1), random.randint(0,size-1))
while end == start: end = (random.randint(0,size-1), random.randint(0,size-1))

m = maze.Maze(size, start, end)
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
# print output to stdout
print m.to_architect_string()
