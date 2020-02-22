#
# calculate average rank for player types that participated in a rr tournament
#
# create violin plot of the data
#

import csv
from os import listdir
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from globals import strategy_dict

path = 'newreps_all/rep_all_axelrod_single-elim_multi_no-noise_rr1000-axelrod-2/'
fig_filename = 'rep_all_axelrod_single-elim_multi_no-noise_rr-ax'

SHOW_PLOT = True

# NUM_TYPES is all of the possible player types
# Possible that some not represented in this data set
NUM_TYPES = len(strategy_dict)
NUM_EACH = 10

# list of lists - one per player type
# each list contains the avg rank for that player type for each tournament
avg_ranks = []
for i in range(NUM_TYPES):
    avg_ranks.append([])

NUM_PTS = 0
files = listdir(path)
for f in files:
    if 'type' not in f and 'top' not in f and 'Store' not in f and '.png' not in f:
        NUM_PTS += 1
        
        fn = open(path + f, 'r')
        reader = csv.reader((line.replace('\0', '') for line in fn))

        lines = []
        for row in reader:
            lines.append(row[1:])
        #remove header lines
        del lines[:5]
        
        # convert the data to numeric types
        lines = [[float(x) if '.' in x else int(x) for x in line] for line in lines]
        
        # sort the data self score
        lines = sorted(lines, key=lambda m: float(m[-6]), reverse=True)
        
        fn.close()

        # list for the avg ranks in one tournament
        tourn_avg_rank = [0] * NUM_TYPES

        for i, line in enumerate(lines):
            # add rank of each individual to total for their player type
            # use i + 1 so that ranks start at 1 rather than 0
            tourn_avg_rank[int(line[-1])] += (i + 1)
            
        for i, e in enumerate(tourn_avg_rank):
            avg_ranks[i].append(float(e)/NUM_EACH)

fout = open(path + 'avg_rank_by_type.csv', 'w')
writer = csv.writer(fout)

for j in avg_ranks:
    writer.writerow(j)
    
fout.close()

indexed_data = list(enumerate(avg_ranks))
indexed_data = [e for e in indexed_data if e[1][0] != 0.0]
indexed_data.sort(key=lambda e: sum(e[1])/len(e[1]))

types_present = [e[0] for e in indexed_data]
avg_ranks = [e[1] for e in indexed_data]

fig_width = 8
if len(types_present) > 40:
    fig_width = 10
    
# create the plot
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(fig_width,6))
parts = ax.violinplot(avg_ranks, points=NUM_PTS, showmeans=True, showextrema=False, showmedians=True, bw_method='silverman')

ax.set_xlabel('IPD Strategy')
ax.set_ylabel('Avg Rank per Tournament')

for pc in parts['bodies']:
    pc.set_facecolor('#2020ff')
    pc.set_alpha(1.0)

med = parts['cmedians']
med.set_edgecolor('#ff0000')
med.set_linewidth(1)

mn = parts['cmeans']
mn.set_edgecolor('#00ff00')
mn.set_linewidth(1)

ax.set_title('IPD Strategies Avg Rank of All Players Sorted by Mean over ' + str(NUM_PTS) + ' Tournaments')
fig_filename += '_avg-rank_by-mean_violinplot.png'

labels = []
for e in types_present:
    labels.append(strategy_dict[e])

ax.set_xticks(np.arange(1, len(labels) + 1))
ax.set_xticklabels(labels, rotation=90)

plt.tight_layout()

fig.savefig(path + fig_filename)

if SHOW_PLOT:
    plt.show()
    
plt.close()
