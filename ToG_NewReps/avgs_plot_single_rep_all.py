#
# create a violin plot from result of post-evolution rr tournaments 
#
# plots the average of all players of each type by representation
# result is a sinlge plot with 4 sections - one for each rep
#
# MUST RUN USING PYTHON3
#

import csv
from os import listdir
from copy import deepcopy
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
path = 'newreps_all/single-rep_pop_single-obj_multi_rr1000/'
sub_paths = ['rep0/', 'rep1/', 'rep2/', 'rep4/']
in_file_name = 'avgs_raw_by_type.csv'

out_path = path
fig_filename = 'single-all_pop_single-elim_multi_no-noise'

# determines the sorted order
#   AVG: sort by mean
#   MAX: sort by max value
SORT = 'AVG'

title_noise = 'Noise: 0.0'
title_train = 'Train: Pop'
title_sort = 'Sort: Mean' if SORT == 'AVG' else 'Sort: Max'

#################################################################################
###
### END -- CHANGE THESE VALUES
###
#################################################################################

if SORT == 'AVG':
    fig_filename += '_avgs_by-mean_violinplot.png'
else:
    fig_filename += '_avgs_by-max_violinplot.png'

# data: each entry in data is a list of the avgs for a single player type
# each avg for a player type is that type's average in a rr tournament
data = []

for sub in sub_paths:
    # reads avgs data from avgs_raw_by_type (created by type_avgs_all_reps.py)
    fn = open(path + sub +in_file_name)
    reader = csv.reader(fn)

    data_curr = [[float(x) for x in row] for row in reader]

    fn.close()
    
    data.append(data_curr)

# data_indexed: each entry is a pair containing the player type and the averages described above
# this is used so that we know which labels to use in the plot
data_indexed = [list(enumerate(e)) for e in data]

# sort by the mean of the averages or the max of the averages
for e in data_indexed:
    if SORT == 'AVG':
        e.sort(key=lambda m: sum(m[1])/len(m), reverse=True)
    else:
        e.sort(key=lambda m: max(m[1]), reverse=True)
    
# eliminate the zero player types from data_indexed
for i, e in enumerate(data_indexed):
    data_indexed[i] = [m for m in e if m[1][0] != 0.0]
    
# remove the 5 lowest scoring player types for each representation
for e in data_indexed:
    del e[-5:]
    
# create list of player types in order to be used to create labels
data = []
label_indices = []
for e in data_indexed:
    for k in e:
        data.append(k[1])
        label_indices.append(k[0])

fig_width = 8
if len(data) > 40:
    fig_width = 12

# number of data points for each strategy (= number of tournaments)
NUM_PTS = len(data[0])

# create the plot
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(fig_width,6))
parts = ax.violinplot(data, points=NUM_PTS, showmeans=True, showextrema=False, showmedians=True, bw_method='silverman')

ax.set_title('Each Representation - ' + title_train + ' - Mean of all Players by Type - ' + title_sort +
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
for e in label_indices:
    labels.append(strategy_dict[e])

ax.set_xticks(np.arange(1, len(labels) + 1))
ax.set_xticklabels(labels, rotation=90)

plt.tight_layout()

fig.savefig(out_path + fig_filename)

if SHOW_PLOT:
    plt.show()
    
plt.close()
