import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D #<-- Note the capitalization!
import numpy as np
import matplotlib.patches as mpatches


with open("DM_runs/TrumpComet/TrumpCometBest2.csv") as f:

    x_vals = []
    y_vals = []
    z_vals = []
    objectives = []
    for line in f:
        currentline = line.split(",")
        x_vals.append(np.float32(currentline[70]))
        y_vals.append(np.float32(currentline[71]))
        z_vals.append(np.float32(currentline[72]))
        objectives.append(int(currentline[74]))


graph_x = []
graph_y = []
colors = []

for person in xrange(len(x_vals)):
    if objectives[person] == 0 or objectives[person] == 1:
        graph_x.append(x_vals[person])
        graph_y.append(y_vals[person])
        if objectives[person] == 0:
            colors.append('black')
        else:
            colors.append('green')
    elif objectives[person] == 2:
        graph_x.append(x_vals[person])
        graph_y.append(z_vals[person])
        colors.append('red')
    else:
        graph_x.append(y_vals[person])
        graph_y.append(z_vals[person])
        colors.append('blue')


fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter(graph_x, graph_y, color = colors, marker='x')

ax.set_title('2 Objectives- with selfish subpopulation')
ax.set_xlabel('Objective 1')
ax.set_ylabel('Objective 2')

obj0 = mpatches.Patch(color='black', label='Selfish')
obj1 = mpatches.Patch(color='green', label='Communal')
obj2 = mpatches.Patch(color='red', label='Cooperative')
obj3 = mpatches.Patch(color='blue', label='Selfless')
ax.legend(handles=[obj0, obj1, obj2, obj3])




# Axes3D.scatter(xs, ys, zs)
# plt.plot(p_front[0], p_front[1])
plt.show()
