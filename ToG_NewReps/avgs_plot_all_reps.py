#
# create a violin plot from result of post-evolution rr tournament for all representations
#
# plots the average of all players of each type
#
# Works for tournaments that include players with different representations
#
# MUST RUN USING PYTHON3
#

import csv
from os import listdir
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import math

from globals import strategy_dict

NUM_TYPES = len(strategy_dict)

SHOW_PLOT = True

#################################################################################
###
### CHANGE THESE VALUES
###
#################################################################################

# path = 'rep1_pop_no-noise_5k/rep1_pop_no-noise_rr1000_results/'
path = 'newreps_all/rep_all_both_single-elim_multi_noise05_rr1000/'
in_file_name = 'avgs_raw_by_type.csv'
path_parts = path.split('/')[1].split('_')
# fig_filename = '_'.join([path_parts[x] for x in range(3)])
fig_filename = 'all_both_single-elim_multi_noise05'
fig_filename += '_avgs_violinplot.png'

title_noise = 'Noise: 0.05'
title_train = 'Train: Axelrod/Pop'
title_sort = 'Sort: Mean'

#################################################################################
###
### END -- CHANGE THESE VALUES
###
#################################################################################

# reads avgs data from avgs_raw_by_type (created by type_avgs_all_reps.py)
fn = open(path + in_file_name)
reader = csv.reader(fn)

# data: each entry in data is a list of the avgs for a single player type
# each avg for a player type is that type's average in a rr tournament
data = [[float(x) for x in row] for row in reader]

# data_indexed: each entry is a pair containing the player type and the averages described above
# this is used so that we know which labels to use in the plot
data_indexed = list(enumerate(data))

# number of data points for each strategy (= number of tournaments)
NUM_PTS = len(data[0])

# sort by the mean of the averages
data.sort(reverse=True, key=lambda m: sum(m)/len(m))
data_indexed.sort(reverse=True, key=lambda m: sum(m[1])/len(m))

# list of the player types for which all entries are 0.0
# this indicates that they did not participate in the tournaments
# we use this to determine which types shoule not appear in the plot
zeros = []
for j, row in enumerate(data):
    if row[0] == 0.0:
        zeros.append(j)
        
fn.close()

# eliminate the zero player types from data_indexed
data_indexed = [data_indexed[k] for k in range(NUM_TYPES) if k not in zeros]
# use the new value of data_indexed to update data
# data will now contain only those player types that participated in the tournaments
data = [row[1] for row in data_indexed]

fig_width = 8
if len(data_indexed) > 40:
    fig_width = 10
    
# create the plot
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(fig_width,6))
parts = ax.violinplot(data, points=NUM_PTS, showmeans=True, showextrema=False, showmedians=True, bw_method='silverman')

ax.set_title(title_train + ' - Mean of all Players by Type - ' + title_sort +
             ' - ' + title_noise + ' - Tournaments: ' + str(NUM_PTS))
ax.set_xlabel('IPD Strategy')
ax.set_ylabel('Avg Score per Tournament')

for pc in parts['bodies']:
    pc.set_facecolor('#2020ff')
    pc.set_alpha(1.0)

med = parts['cmedians']
med.set_edgecolor('#ff0000')
med.set_linewidth(1)

mn = parts['cmeans']
mn.set_edgecolor('#00ff00')
mn.set_linewidth(1)

labels = []
for e in data_indexed:
    labels.append(strategy_dict[e[0]])

ax.set_xticks(np.arange(1, len(labels) + 1))
ax.set_xticklabels(labels, rotation=90)

plt.tight_layout()

fig.savefig(path + fig_filename)

if SHOW_PLOT:
    plt.show()
    
plt.close()
