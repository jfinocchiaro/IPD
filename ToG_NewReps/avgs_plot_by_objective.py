#
# create a violin plot from result of post-evolution rr tournaments 
#
# plots the average of all evolved players of each objective/objective-pair
# each standard player type counts as its own objective as well
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

objective_map = {0:'Selfish', 1:'Communal', 2:'Cooperative', 3:'Selfless', 4:'Self', 5:'MinDiff', 
                 6: 'Always C', 7: 'Always D', 8: 'TFT', 9: 'STFT', 10: 'Pavlov', 11: 'Spiteful', 
                 12: 'Random', 13: 'CD', 14: 'DDC', 15: 'CCD', 16: 'TF2T', 17: 'Soft Maj', 
                 18: 'Hard Maj', 19: 'HTFT', 20: 'Naive', 21: 'Remorseful', 22: 'Gradual'}

SHOW_PLOT = True

#################################################################################
###
### CHANGE THESE VALUES
###
#################################################################################

# path = 'rep1_pop_no-noise_5k/rep1_pop_no-noise_rr1000_results/'
path = 'newreps_all/rep_all_pop_single-elim_multi_no-noise_rr1000-2/'
in_file_name = 'avgs_by_obj.csv'

# out_path = 'newreps_all/single-rep_axelrod_single-obj_multi_rr1000/'
out_path = path
fig_filename = 'rep-all_pop_single-multi_no-noise'
fig_filename += '_avgs_by_obj_L64L8M8FSM.png'

# determines the sorted order
#   AVG: sort by mean
#   MAX: sort by max value
SORT = 'AVG'

title_noise = 'Noise: 0.0'
title_train = 'Train: Pop'
title_reps = 'L64 L8 M8 FSM'
title_sort = 'Sort: Mean' if SORT == 'AVG' else 'Sort: Max'


#################################################################################
###
### END -- CHANGE THESE VALUES
###
#################################################################################

# data: each entry in data is a list of the avgs for a single player type
# each avg for a player type is that type's average in a rr tournament
data = []

# reads avgs data from avgs_raw_by_type (created by type_avgs_all_reps.py)
fn = open(path + in_file_name)
reader = csv.reader(fn)

data = [[float(x) for x in row] for row in reader]

fn.close()

# data_indexed: each entry is a pair containing the player type and the averages described above
# this is used so that we know which labels to use in the plot
data_indexed = list(enumerate(data))

# sort by the mean of the averages or the max of the averages
if SORT == 'AVG':
    data_indexed.sort(key=lambda m: sum(m[1])/len(m), reverse=True)
else:
    data_indexed.sort(key=lambda m: max(m[1]), reverse=True)

# create data (used in plot) from data_indexed by eliminating the indices
# create list of player types to be used to create labels
data = []
label_indices = []
for e in data_indexed:
    data.append(e[1])
    label_indices.append(e[0])

fig_width = 8
if len(data) > 40:
    fig_width = 12

# number of data points for each strategy (= number of tournaments)
NUM_PTS = len(data[0])

# create the plot
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(fig_width,6))
parts = ax.violinplot(data, points=NUM_PTS, showmeans=True, showextrema=False, showmedians=True, bw_method='silverman')

# ax.set_title('IPD Strategies Mean of all Players by Objective Ranked by Mean over ' + str(NUM_PTS) + ' Tournaments')
ax.set_title('Representations: ' + title_reps + ' - ' + title_train + ' - Mean of all Players by Objective\n' + 
             title_sort + ' - ' + title_noise + ' - Tournaments: ' + str(NUM_PTS))
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
    labels.append(objective_map[e])

ax.set_xticks(np.arange(1, len(labels) + 1))
ax.set_xticklabels(labels, rotation=90)

plt.tight_layout()

fig.savefig(out_path + fig_filename)

if SHOW_PLOT:
    plt.show()
    
plt.close()
