import pulp

prob = pulp.LpProblem('wildfires', pulp.LpMinimize)

evac_transit = []
transits = []

with open('evac_transit_flow.csv', newline='') as f:
    reader = csv.reader(f)
    reader = list(reader)

evac_transit = [[int(i) for i in row] for row in reader] # evac goes to transit nodes, safe node is transit node 1

with open('transits_flow.csv', newline='') as f:
    reader = csv.reader(f)
    reader = list(reader)

transits = [[int(i) for i in row] for row in reader] #safe node is transit node 1

prob.solve()

for i, p in enumerate(prob.variables()):
    print(p.name, ":", p.varValue)
