from gurobipy import *
import csv
import random
import numpy as np

random.seed(100)

# Define the Minimization Problem
prob = Model('wildfires')
# prob = pulp.LpProblem('wildfires', pulp.LpMinimize)
# hi :)
# Define the number of each node
evac_count = 31    #N
transit_count = 10 #M

total_pop = 10000
region_pop = int(total_pop/4)
evac_pop = int(region_pop / evac_count)

# Define the graph network of both evacuation leaves to transits and intertransit travel
evac_transit = []
transits = []

with open('evac_transit.csv', newline='') as f:
    reader = csv.reader(f)
    reader = list(reader)

evac_transit = [[int(i) - int(j == 0 or j == 1) for j,i in enumerate(row)] for row in reader] # evac goes to transit nodes, safe node is transit node 1
print(evac_transit[0])
with open('transits.csv', newline='') as f:
    reader = csv.reader(f)
    reader = list(reader)

transits = [[int(i) - int(j == 0 or j == 1) for j,i in enumerate(row)] for row in reader] #safe node is transit node 1

# Start Node | End Node | Travel Time | Capacity | Unsafe Time (if possible)

# FIXME edit the random length
# lvu = [ [random.randint(1, transits[i][4]) for _ in range(evac_count)] for i in range(transit_count)]
# lvu = [[0 * evac_count]] * transit_count
lvu = [ [0]*transit_count for _ in range(evac_count) ]
print(len(lvu), len(lvu[0]))
max_lvu = 0
for i in range(evac_count):
    for j in range(transit_count):
        max_lvu = max(max_lvu, lvu[i][j])+ region_pop/5
w = max_lvu + region_pop/5 #vac_pop
# H = int(max_lvu + region_pop/5)
H = 100

print(len(transits), len(transits[0]))
due_times = [transits[i][4] for i in range(transit_count)]
transit_arc_capacity = [transits[i][2] for i in range(transit_count)]

dvs = [5 for _ in range(31)] # TODO: fill in explicitly maybe (size 31)
leaf_descendants = [[], [], [], [], [], [], [], [], [], []]
evac_parent = {}
for evac, transit, travel, capacity in evac_transit:
    evac_parent[evac] = transit
    lvu[evac][transit] = travel
    leaf_descendants[transit].append(evac)
transit_parent = {}
for transit_out, transit_in, transit, capacity, due_time in transits:
    transit_parent[transit_out] = transit_in
    for leaf in leaf_descendants[transit_in]:
        lvu[leaf][transit_out] = lvu[leaf][transit_in] + transit
        leaf_descendants[transit_out].append(leaf)

z = prob.addVars(evac_count)
s = prob.addVars(evac_count, lb=0, ub=H)
h = prob.addVars(evac_count, lb=0, ub=5)
e = prob.addVars(evac_count)
# ind = prob.addVars(evac_count, H, vtype=GRB.BINARY)
phi_v_t = prob.addVars(evac_count, H)
phi_u_t = prob.addVars(transit_count, H)
x = prob.addVar()
prob.setObjective(x, GRB.MINIMIZE)
print(phi_v_t)
for i in range(evac_count):
    prob.addConstr(x >= evac_pop * (e[i]-dvs[i]))
    prob.addConstr(e[i] == s[i] + evac_pop*z[i])
    prob.addConstr(h[i]*z[i] == 1)
    for t in range(H):
        
        # prob.addConstr(t - s[i] >= 0 - H * (1-ind[i][t]))
        # prob.addConstr(t - s[i] <= evac_pop * z[i] + H * (1-ind[i][t]))
        #prob.addConstr(phi_v_t[i][t] == h[i]*ind[i][t])
        print(H)
        print(t)
        print(s[i])
        print(z[i])
        # print(phi_v_t[0, 0])
        #print(phi_v_t[i, t])
        prob.addConstr(phi_v_t[i, t] == h[i]*(t >= s[i] and t <= (s[i] + evac_pop*z[i])))

for i in range(transit_count):
    for t in range(H):
        prob.addConstr(phi_u_t[i][t] == sum(phi_v_t[j][t-lvu[j][i]] for j in leaf_descendants[i]))
        prob.addConstr(phi_u_t[1][t] <= transit_arc_capacity[i])

# for i in range(1, evac_count+1):
#     prob += h[i] <= 5 * ind[i][t]

prob.optimize()
# prob.solve(pulp.getSolver('GUROBI'))

for i, p in enumerate(prob.variables()):
    print(p.name, ":", p.varValue)
