import pulp
import csv
import random

random.seed(100)

# Define the Minimization Problem
prob = pulp.LpProblem('wildfires', pulp.LpMinimize)
# hi :)
# Define the number of each node
evac_count = 31    #N
transit_count = 10 #M

total_pop = 15000
region_pop = total_population/4
evac_pop = region_population / evac_count

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

s = pulp.LpVariable.dicts("s", range(1, evac_count + 1), cat='Integer') # Should have evacuation node count size (N)
h = pulp.LpVariable.dicts("h", range(1, evac_count + 1), cat='Integer') # Should have transit node count size (N)

# FIXME edit the random length
prob += max(s[i] + h[i] / evac_pop - min(transits[j][4] - random.randint(1, transits[j][4] + 1) for j in range(1, transit_count + 1)) for i in range(1, evac_count + 1))

prob.solve()

for i, p in enumerate(prob.variables()):
    print(p.name, ":", p.varValue)
