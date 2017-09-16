from gurobipy import *
import pandas as pd

num_acc = 42
startx = 0
endx = 4
starty = 0
endy = 4
acc_per_tile = 7

# first 48 accelerators
data = pd.read_csv('all.csv', index_col=False)
accelerators = data.drop('Workload', axis=1).sum(axis=0).sort_values(ascending=False).index[:num_acc]
assert len(accelerators) == num_acc

# create comm cost matrix
cost_mat = {}
for acc1 in accelerators:
    for acc2 in accelerators:
        cost_mat[acc1, acc2] = 0
for acc1 in accelerators:
    for acc2 in accelerators:
        for _, row in data.iterrows():
            if pd.notnull(row[acc1]) and pd.notnull(row[acc2]):
                cost_mat[acc1, acc2] += 1

# simulate 160 accelerators
# accelerators = ['A'+str(x) for x in range(160)]

# on a 4x4 chip
locationX = range(startx, endx)
locationY = range(starty, endy)

m = Model('layout')

locations = m.addVars(accelerators, locationX, locationY, vtype=GRB.BINARY, name='locations')

coeffX = {(acc, i, j): i for acc in accelerators for i in locationX for j in locationY}
coeffY = {(acc, i, j): j for acc in accelerators for i in locationX for j in locationY}

locX = m.addVars(accelerators, vtype=GRB.INTEGER, name='locX')
locY = m.addVars(accelerators, vtype=GRB.INTEGER, name='locY')
m.addConstrs((locX[acc] == locations.prod(coeffX, acc, '*', '*') for acc in accelerators), name='bin2decx')
m.addConstrs((locY[acc] == locations.prod(coeffY, acc, '*', '*') for acc in accelerators), name='bin2decy')

distX = m.addVars(accelerators, accelerators, name='distX')
distY = m.addVars(accelerators, accelerators, name='distY')
distance = m.addVars(accelerators, accelerators, name='distance')
for acc1 in accelerators:
    for acc2 in accelerators:
        distance[acc1, acc2] = (distX[acc1, acc2] + distY[acc1, acc2]) * cost_mat[acc1, acc2]

# abs
m.addConstrs((locX[acc1] - locX[acc2] <= distX[acc1, acc2] for acc1 in accelerators for acc2 in accelerators), name='absx1')
m.addConstrs((locX[acc2] - locX[acc1] <= distX[acc1, acc2] for acc1 in accelerators for acc2 in accelerators), name='absx2')
m.addConstrs((locY[acc1] - locY[acc2] <= distY[acc1, acc2] for acc1 in accelerators for acc2 in accelerators), name='absy1')
m.addConstrs((locY[acc2] - locY[acc1] <= distY[acc1, acc2] for acc1 in accelerators for acc2 in accelerators), name='absy2')

# each accelerator only appear once
m.addConstrs((locations.sum(i, '*', '*') == 1 for i in accelerators), name='acc')

# each tile has acc_per_tile accelrators
none_or_all = m.addVars(locationX, locationY, vtype=GRB.BINARY, name='none_or_all')
m.addConstrs((locations.sum('*', i, j) == acc_per_tile * none_or_all[i, j] for i in locationX for j in locationY), name='tile')

# minimize distance
m.setObjective(distance.sum('*', '*'), GRB.MINIMIZE)

m.optimize()

res = pd.DataFrame()
for acc in accelerators:
    res.loc[acc, 'locX'] = locX[acc].x
    res.loc[acc, 'locY'] = locY[acc].x
print res
res.to_csv('layout.csv')
