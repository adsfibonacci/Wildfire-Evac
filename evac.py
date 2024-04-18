import pulp

prob = pulp.LpProblem('wildfires', pulp.LpMinimize)

evac_transit = []
transit_transit = []
transit_safe = []

with open('evac_transit_flow.csv', newline='') as f:
    reader = csv.reader(f)
    reader = list(reader)

evac_transit = [[int(i) for i in row] for row in reader]

with open('transit_transit_flow.csv', newline='') as f:
    reader = csv.reader(f)
    reader = list(reader)

transit_transit = [[int(i) for i in row] for row in reader]

with open('transit_safe_flow.csv', newline='') as f:
    reader = csv.reader(f)
    reader = list(reader)

transit_safe = [[int(i) for i in row] for row in reader]

prob.solve()

for i, p in enumerate(prob.variables()):
    print(p.name, ":", p.varValue)
