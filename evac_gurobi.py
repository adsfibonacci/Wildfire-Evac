from gurobipy import *
import csv
import random
import numpy as np
import time

start_time = time.time()

# Define the Minimization Problem
prob = Model('wildfires')
# prob = pulp.LpProblem('wildfires', pulp.LpMinimize)
# hi :)
# Define the number of each node
#evac_count = 18   #N
#transit_count = 9 #M

total_pop = 5000

# region_pop = [int(float(31/70)*region_pop), int(float(5/70)*region_pop), int(float(18/70)*region_pop), int(float(16/70)*region_pop) ]
# evac_count = [31, 5, 18, 16]
# transit_count = [9, 3, 8, 9]

evac_count = {'soa1': 31, 'sob1': 5, 'soc1': 18, 'sod1': 16}
evac_pop = int(total_pop / sum(evac_count.values()))
transit_count = {'soa1': 10, 'sob1': 4, 'soc1': 9, 'sod1': 10}

# Define the graph network of both evacuation leaves to transits and intertransit travel
evac_transit = []
transits = []

region = 'sod1' # SPECIFY REGION FOR RUN HERE
region_pop = evac_count[region] * evac_pop
print(f'region pop: {region_pop}')
print(f'evac pop: {evac_pop}')

with open(f'{region}_evac_transit.csv', newline='') as f:
    reader = csv.reader(f)
    reader = list(reader)

evac_transit = [[float(i) - int(j == 0 or j == 1) for j,i in enumerate(row)] for row in reader] # evac goes to transit nodes, safe node is transit node 1
evac_capacity = [evac_transit[i][3] for i in range(evac_count[region])]
evac_distance = [int(evac_transit[i][2] * 100) for i in range(evac_count[region])]
evac_parent = [int(evac_transit[i][1]) for i in range(evac_count[region])]
# print(evac_transit[0])
with open(f'{region}_transit.csv', newline='') as f:
    reader = csv.reader(f)
    reader = list(reader)

transits = [[float(i) - int(j == 0 or j == 1) for j,i in enumerate(row)] for row in reader] #safe node is transit node 1
due_time = [transits[i][4] * 100 for i in range(transit_count[region])]
transit_capacity = [transits[i][3] for i in range(transit_count[region])]
min_capacity = min(min(evac_capacity), min(transit_capacity))
print(f'min_capacity: {min_capacity}')
transit_distance = [int(transits[i][2] * 100) for i in range(transit_count[region])]
transit_parent = [int(transits[i][1]) for i in range(transit_count[region])]
# Start Node | End Node | Travel Time | (Capacity or Max Flow) | Unsafe Time (if possible)

# FIXME edit the random length
# lvu = [ [random.randint(1, transits[i][4]) for _ in range(evac_count[region])] for i in range(transit_count[region])]
# lvu = [[0 * evac_count[region]]] * transit_count[region]

# form sets of leaf descendants for each transit node
leaf_descendants = [[] for _ in range(transit_count[region])]
for i in range(evac_count[region]):
    leaf_descendants[evac_parent[i]].append(i)

# # discover transit parents
# transit_parent = {}
# for i in range(transit_count[region]):
#     par = transits[i][1]
#     transit_parent[i] = par

# pass leaves upwards
for i in range(transit_count[region]):
    par = transit_parent[i]
    while par != -1:
        for leaf in leaf_descendants[i]:
            leaf_descendants[par].append(leaf)
        par = transit_parent[par]

lvu = [ [-1]*transit_count[region] for _ in range(evac_count[region]) ]
max_lvu = -1
# effectively "time each evac node needs to have everyone in motion to stay safe"
dv = [100000 for _ in range(evac_count[region])] # 1000 is intended as guaranteed upper bound that will be lowered
# find length to each transit node for path of each evac node
for i in range(evac_count[region]):
    par = evac_parent[i]
    cur_dist = evac_distance[i]
    lvu[i][par] = cur_dist
    dv[i] = min(dv[i], due_time[par] - lvu[i][par])
    # update parent
    par = transit_parent[par]
    while par != -1:
        cur_dist += transit_distance[par]
        lvu[i][par] = cur_dist
        max_lvu = max(max_lvu, lvu[i][par])
        dv[i] = min(dv[i], due_time[par] - lvu[i][par])
        # update parent
        par = transit_parent[par]
    print(dv[i])

# print(len(lvu), len(lvu[0]))
# max_lvu = 0
# for i in range(evac_count[region]):
#     for j in range(transit_count[region]):
#         max_lvu = max(max_lvu, lvu[i][j]) + region_pop/5
H = int(max_lvu + (region_pop/min_capacity))
# H = 100
print(f'H: {H}')

# print(len(transits), len(transits[0]))





# evac_parent = {}
# for evac, transit, travel, capacity in evac_transit:
#     evac_parent[evac] = transit
#     lvu[evac][transit] = travel
#     leaf_descendants[transit].append(evac)
# transit_parent = {}
# for transit_out, transit_in, transit, capacity, due_time in transits:
#     transit_parent[transit_out] = transit_in
#     for leaf in leaf_descendants[transit_in]:
#         lvu[leaf][transit_out] = lvu[leaf][transit_in] + transit
#         leaf_descendants[transit_out].append(leaf)

x = prob.addVar(name='x')
prob.setObjective(x, GRB.MINIMIZE)

z = prob.addVars(evac_count[region], name='z')
s = prob.addVars(evac_count[region], lb=0, name='s')
h = prob.addVars(evac_count[region], lb=0, name='h')
e = prob.addVars(evac_count[region], name='e')
for i in range(evac_count[region]):
    # s[i].UB = H - (evac_pop / evac_capacity[i])
    h[i].UB = evac_capacity[i]
    e[i].UB = H

ind = prob.addVars(evac_count[region], H, vtype=GRB.BINARY)

phi_v_t = prob.addVars(evac_count[region], H)
phi_u_t = prob.addVars(transit_count[region], H)

# print(phi_v_t)
for i in range(evac_count[region]):
    # prob.addConstr(x >= evac_pop * (e[i]-dv[i]))
    prob.addConstr(x >= e[i]-dv[i])
    prob.addConstr(e[i] == s[i] + evac_pop*z[i])
    prob.addConstr(h[i]*z[i] == 1)
    for t in range(H):
        
        # prob.addConstr(t - s[i] >= 0 - H * (1-ind[i][t]))
        # prob.addConstr(t - s[i] <= evac_pop * z[i] + H * (1-ind[i][t]))
        # prob.addConstr(phi_v_t[i][t] == h[i]*ind[i][t])
        # print(H)
        # print(t)
        # print(s[i])
        # print(z[i])
        # print(phi_v_t[0, 0])
        # print(phi_v_t[i, t])
        # prob.addConstr(phi_v_t[i, t] == h[i]*(t >= s[i] and t <= (s[i] + evac_pop*z[i])))
        prob.addGenConstrIndicator(ind[i, t], False, t <= s[i] - 1)
        prob.addGenConstrIndicator(ind[i, t], False, t >= s[i] + e[i] + 1)
        prob.addConstr(phi_v_t[i, t] == h[i]*ind[i, t])

for i in range(transit_count[region]):
    for t in range(H):
        valid_descendants = []
        for j in leaf_descendants[i]:
            if t - lvu[j][i] < 0:
                continue
            valid_descendants.append(j)

        prob.addConstr(phi_u_t[i, t] == sum(phi_v_t[j, t-lvu[j][i]] for j in valid_descendants))
        prob.addConstr(phi_u_t[i, t] <= transit_capacity[i])

# for i in range(1, evac_count[region]+1):
#     prob += h[i] <= 5 * ind[i][t]

prob.optimize()
# prob.solve(pulp.getSolver('GUROBI'))

with open(f'{region}_output.txt', 'w') as outfile:
    outfile.write('cpu clock time: ' + str(time.time() - start_time))
    if prob.status == GRB.Status.OPTIMAL:
        outfile.write('\n Obj Val: %g\n' % prob.objVal)
        for v in prob.getVars():
            # if v.x != 0:
            outfile.write('%s %g\n' % (v.varName, v.x))
    else:
        outfile.write('No solution\n')

