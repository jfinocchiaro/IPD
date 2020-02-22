#
# create a violin plot from result of post-evolution rr tournament for all representations
#
# plots the rank of best player of each type over all runs
#

import csv
from os import listdir
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import math

# this is the dictionary mapping player types to descriptive strings
from globals import strategy_dict

# total number of possible types -- some may not be present
NUM_TYPES = len(strategy_dict)

# path = 'rep1_pop_no-noise_5k/rep1_pop_no-noise_rr1000_results/'
path = 'newreps_all/rep_all_axelrod_single-elim_multi_no-noise_rr1000-axelrod-2/'
in_file_name = 'best_raw_by_type.csv'
path_parts = path.split('/')[1].split('_')
# fig_filename = '_'.join([path_parts[x] for x in range(3)])
fig_filename = 'rep_all_pop_single-elim_multi_no-noise_rr-ax'

SHOW_PLOT = True

fn = open(path + in_file_name)
reader = csv.reader(fn)

# convert reader into a list of lists of floats
data = [[float(x) for x in row] for row in reader]


# list of lists of data -- one for each player type
# each list is [p_type, [list of values for p_type]]
data_indexed = list(enumerate(data))

# number of data points for each strategy (= number of tournaments)
NUM_PTS = len(data_indexed[0][1])

# contains a list for each player type
# each player type list will contain rank of best player of that type for each tournament
# NOTE: each player type list is initially augmented with the player type -- removed later
ranks = [[i, []] for i in range(NUM_TYPES)]

# convert the score data into rank data by:
#   NOTE: number of tournaments = NUM_PTS
#   for each tournament, create a temp list of (p_type, best score) pairs
#   sort that list by best score -- this puts the p_types in rank order
#   append to the rank list for each player type, it's rank in the current tournament
#   repeat for next tournament
for k in range(NUM_PTS):
    curr = []
    for j in range(NUM_TYPES):
        curr.append((data_indexed[j][0], data_indexed[j][1][k]))
    curr.sort(key=lambda e: e[1], reverse=True)
    
    for i, m in enumerate(curr):
        ranks[m[0]][1].append(i)

# determine which player types didn't participate in the tournaments
zeros = []
for j, row in enumerate(data_indexed):
    if row[1][0] == 0.0:
        zeros.append(j)

# this is the list of player types that did participate in the tournaments
types = [k for k in range(NUM_TYPES) if k not in zeros]

fn.close()

# eliminate from the ranks list the lists for those types that didn't participate
ranks = [ranks[k] for k in range(NUM_TYPES) if k in types]

# sort ranks according to sum of ranks by type
ranks.sort(key=lambda m: sum(m[1]))

# list of the types that participated in the tournaments in order by sorted ranks
sorted_types = [m[0] for m in ranks]

# eliminate the p_type values augmenting entries in the ranks list
ranks = [m[1] for m in ranks]

fig_width = 8
if len(sorted_types) > 40:
    fig_width = 10
    
# create the plot
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(fig_width,6))
parts = ax.violinplot(ranks, points=NUM_PTS, showmeans=True, showextrema=False, showmedians=True, bw_method='silverman')

ax.set_xlabel('IPD Strategy')
ax.set_ylabel('Best Rank per Tournament')

for pc in parts['bodies']:
    pc.set_facecolor('#2020ff')
    pc.set_alpha(1.0)

med = parts['cmedians']
med.set_edgecolor('#ff0000')
med.set_linewidth(1)

mn = parts['cmeans']
mn.set_edgecolor('#00ff00')
mn.set_linewidth(1)

ax.set_title('IPD Strategies Rank of Best Scores Sorted by Mean over ' + str(NUM_PTS) + ' Tournaments')
fig_filename += '_best-rank_by-mean_violinplot.png'

labels = []
for e in sorted_types:
    labels.append(strategy_dict[e])

ax.set_xticks(np.arange(1, len(labels) + 1))
ax.set_xticklabels(labels, rotation=90)

plt.tight_layout()

fig.savefig(path + fig_filename)

if SHOW_PLOT:
    plt.show()
    
plt.close()
