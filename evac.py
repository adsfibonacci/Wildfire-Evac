import pulp
import csv
import random
import numpy as np

random.seed(100)

# Define the Minimization Problem
prob = pulp.LpProblem('wildfires', pulp.LpMinimize)
# hi :)
# Define the number of each node
evac_count = 31    #N
transit_count = 9 #M

total_pop = 15000
region_pop = total_pop/4
evac_pop = region_pop / evac_count

# Define the graph network of both evacuation leaves to transits and intertransit travel
evac_transit = []
transits = []

with open('evac_transit.csv', newline='') as f:
    reader = csv.reader(f)
    reader = list(reader)

evac_transit = [[int(i) for i in row] for row in reader] # evac goes to transit nodes, safe node is transit node 1

with open('transits.csv', newline='') as f:
    reader = csv.reader(f)
    reader = list(reader)

transits = [[int(i) for i in row] for row in reader] #safe node is transit node 1

# Start Node | End Node | Travel Time | Capacity | Unsafe Time (if possible)

# FIXME edit the random length
luv = [ random.randint(1, transits[j][4]) for j in range(transit_count)]
H = int(max(luv[i] for i in range(transit_count)) + region_pop/5)
w = 1/evac_pop

s = pulp.LpVariable.dicts("s", range(1, evac_count + 1), lowBound=0, upBound=H - evac_pop/5, cat='Integer') # Should have evacuation node count size (N)

h = pulp.LpVariable.dicts("h", range(1, evac_count + 1), lowBound=0, upBound=5, cat='Integer') # Should have transit node count size (N)

d = pulp.LpVariable("d", lowBound=0, cat='Integer')
ind = pulp.LpVariable.dicts("time-indicator", (range(1, evac_count + 1), range(H)), cat='Binary')

prob += d

for i in range(1, evac_count+1):
    prob += d >= s[i] + w * h[i] - min( transits[j][4] - luv[j] for j in range(transit_count))
    for t in range(H):
        prob += t - s[i] >= 0 - H * (1-ind[i][t])
        prob += t - s[i] <= w * h[i] + H * (1-ind[i][t])

for i in range(1, evac_count+1):
    prob += h[i] <= 5 * ind[i][t]

prob.solve(pulp.getSolver('GUROBI'))

for i, p in enumerate(prob.variables()):
    print(p.name, ":", p.varValue)
