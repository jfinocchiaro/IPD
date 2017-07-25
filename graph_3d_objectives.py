import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D #<-- Note the capitalization!
import numpy as np
import matplotlib.patches as mpatches


with open("DM_runs/LOO3Objectives/LOO3objCometAll.csv") as f:

    x_vals = []
    y_vals = []
    z_vals = []


    for line in f:
        currentline = line.split(",")
        x_vals.append(np.float32(currentline[70]))
        y_vals.append(np.float32(currentline[71]))
        z_vals.append(np.float32(currentline[72]))




fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.scatter(x_vals, y_vals, z_vals, c='b', marker='x')

ax.set_title('3 Objectives- Leave-One-Out All Trials')
ax.set_xlabel('Personal score')
ax.set_ylabel('Opponent score')
ax.set_zlabel('Cooperation score')



# Axes3D.scatter(xs, ys, zs)
# plt.plot(p_front[0], p_front[1])
plt.show()
